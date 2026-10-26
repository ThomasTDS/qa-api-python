import json
import os
import re
import warnings
from collections.abc import Generator
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import allure
import pytest
import requests
from hypothesis import settings
from pydantic import ValidationError

from api.auth_api_client import AuthApiClient
from api.booking_api_client import BookingApiClient
from api.health_api_client import HealthApiClient
from models.booking import Booking

# Steps compartilhados entre features (token, Basic auth, booking criado, health check, 403, 405 e 500).
pytest_plugins = ["steps.common_steps"]

# Perfis do Hypothesis (testes de propriedade): o padrão gera 100 exemplos por
# teste, para rodar rápido localmente; o perfil "ci", ativado no workflow com
# --hypothesis-profile=ci, gera 1000, já que no CI sobra tempo e nada acessa a rede.
# O prazo por exemplo (deadline) fica desligado: ele serve para achar código
# lento, mas aqui o tempo varia com a máquina (um mesmo exemplo levou 318 ms na
# primeira vez e 2 ms na repetição), e o Hypothesis acusava o teste como instável.
settings.register_profile("default", deadline=None)
settings.register_profile("ci", max_examples=1000, deadline=None)
# No teste de mutação, cada teste roda uma vez por mutante; 25 exemplos bastam
# para perceber a alteração sem deixar a execução lenta demais.
settings.register_profile("mutacao", max_examples=25, deadline=None)

BASE_URL = os.environ.get("BASE_URL", "https://restful-booker.herokuapp.com")
# O padrão são as credenciais públicas da documentação da restful-booker, para
# o projeto rodar sem configuração. Outro ambiente pode usar credenciais próprias.
API_USERNAME = os.environ.get("API_USERNAME", "admin")
API_PASSWORD = os.environ.get("API_PASSWORD", "password123")
# Tempo máximo de cada resposta, em milissegundos. O padrão de 3 s é o dobro
# do pior tempo medido na API pública (cerca de 1,4 s); o CI usa 500 ms contra
# a API local, onde cada resposta leva poucos milissegundos.
RESPONSE_TIME_LIMIT_MS = int(os.environ.get("RESPONSE_TIME_LIMIT_MS", "3000"))


FEATURES_DIR = Path(__file__).parent / "features"
STEPS_DIR = Path(__file__).parent / "steps"


# Cada cenário tem uma tag @TC-XXX na linha logo acima de "Cenário:". Devolve,
# para cada TC, o arquivo .feature e o número da linha do cenário. É a fonte
# usada para registrar os marcadores e para conferir a matriz em docs/.
def tc_scenarios() -> dict[str, tuple[str, int]]:
    found: dict[str, tuple[str, int]] = {}
    for path in sorted(FEATURES_DIR.glob("*.feature")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            for tc in re.findall(r"@(TC-\d{3})\b", line):
                assert tc not in found, f"{tc} aparece em mais de um cenário"
                found[tc] = (path.name, index + 2)
    return found


def pytest_configure(config: pytest.Config) -> None:
    for tc in tc_scenarios():
        config.addinivalue_line("markers", f"{tc}: id do test case, ver docs/test-cases.md")


class Context:
    def __init__(self, session: requests.Session) -> None:
        self.session = session
        self.auth_client = AuthApiClient(session, BASE_URL, API_USERNAME, API_PASSWORD)
        self.booking_client = BookingApiClient(session, BASE_URL)
        self.health_client = HealthApiClient(session, BASE_URL)
        self.token: str | None = None
        # Credenciais de Basic auth, alternativa ao token no cookie.
        self.basic_auth: tuple[str, str] | None = None
        self.booking_id: int | None = None
        self.booking_data: Booking | None = None
        self.last_response: requests.Response | None = None
        # Respostas acima do limite de tempo, anotadas por um hook da sessão e
        # cobradas ao fim do cenário (pytest_bdd_after_scenario).
        self.slow_responses: list[str] = []
        session.hooks["response"].append(self._check_elapsed)

    def _check_elapsed(self, response: requests.Response, *args: Any, **kwargs: Any) -> None:
        elapsed_ms = response.elapsed.total_seconds() * 1000
        if elapsed_ms > RESPONSE_TIME_LIMIT_MS:
            path = urlsplit(response.url).path
            self.slow_responses.append(f"{response.request.method} {path} levou {elapsed_ms:.0f} ms")

    # Atalho para os steps de verificação: falha com mensagem clara se o
    # cenário chegou ao Then sem ter feito nenhuma requisição.
    @property
    def response(self) -> requests.Response:
        assert self.last_response is not None, "nenhuma requisição foi feita neste cenário"
        return self.last_response

    # Cenários sem token mandam o cookie vazio, para testar o bloqueio da API.
    @property
    def token_or_empty(self) -> str:
        return self.token or ""


# Verificação de saúde, feita uma vez por sessão, antes do primeiro teste de
# integração. Com a API fora do ar, cada teste de integração aparece como
# ERROR com o motivo, em vez de fazer as próprias chamadas, esperar o timeout
# e ser repetido pelo retry. O pytest guarda a falha da fixture e a repete
# nos testes seguintes, então o /ping não é chamado de novo.
@pytest.fixture(scope="session")
def api_disponivel() -> None:
    problem: str | None = None
    with requests.Session() as session:
        try:
            response = HealthApiClient(session, BASE_URL).ping()
            if response.status_code != 201:
                problem = f"o /ping respondeu {response.status_code}"
        except requests.RequestException as error:
            problem = str(error)
    # Fora do except de propósito: assim a falha não carrega a exceção de
    # conexão encadeada, que faria o retry (only_rerun) repetir o teste.
    if problem is not None:
        pytest.fail(f"API indisponível em {BASE_URL}: {problem}", pytrace=False)


# Roda na preparação de cada teste da pasta steps/ (os de integração). No
# pytest-bdd, a fixture context só é pedida pelos steps, já durante o teste;
# a verificação precisa vir antes, para a falha aparecer como ERROR. Os
# testes unitários não passam por aqui e rodam mesmo sem a API.
@pytest.fixture(autouse=True)
def _exige_api_nos_testes_de_integracao(request: pytest.FixtureRequest) -> None:
    if request.node.path.is_relative_to(STEPS_DIR):
        request.getfixturevalue("api_disponivel")


@pytest.fixture
def context() -> Generator[Context, None, None]:
    session = requests.Session()
    ctx = Context(session)
    yield ctx

    if ctx.booking_id is not None:
        try:
            cleanup_token = ctx.auth_client.get_valid_token()
            ctx.booking_client.delete_booking(ctx.booking_id, cleanup_token)
        except (requests.RequestException, ValidationError) as error:
            # Falha de rede ou de autenticação na limpeza não muda o resultado
            # do teste, que já verificou o que precisava, mas deixa o booking
            # para trás na API pública. O aviso aparece no resumo do pytest.
            # (Se o próprio cenário já removeu o booking, a API só devolve um
            # status de erro, sem exceção, e nada é avisado.)
            warnings.warn(f"booking {ctx.booking_id} não foi removido na limpeza: {error}", stacklevel=1)

    session.close()


EVIDENCE_TITLE = "Evidência da falha"
EVIDENCE_KEY = pytest.StashKey[str]()


def _evidence(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        body = response.text
    evidence = {
        "url": response.url,
        "status": response.status_code,
        "reason": response.reason,
        "headers": dict(response.headers),
        "body": body,
    }
    return json.dumps(evidence, indent=2, ensure_ascii=False)


# Quando um step falha, anexa ao relatório Allure a última resposta da API
# (URL, status, headers e corpo), que já serve de evidência para uma issue. É
# este gancho do pytest-bdd que recebe a fixture context: no pytest-bdd quem
# pede a context são os steps, então ela não aparece nos argumentos do teste.
# Ao fim de cada cenário, falha o teste se alguma resposta passou do limite de
# tempo, listando todas de uma vez. Roda dentro do teste, então a falha conta
# como do cenário (e não da limpeza); por ser uma falha de asserção, e não de
# rede, o retry não a repete.
def pytest_bdd_after_scenario(request: pytest.FixtureRequest, **_: Any) -> None:
    ctx = request.getfixturevalue("context")
    if isinstance(ctx, Context) and ctx.slow_responses:
        lista = "; ".join(ctx.slow_responses)
        pytest.fail(f"Resposta acima do limite de {RESPONSE_TIME_LIMIT_MS} ms: {lista}", pytrace=False)


def pytest_bdd_step_error(request: pytest.FixtureRequest, step_func_args: dict[str, Any], **_: Any) -> None:
    ctx = step_func_args.get("context")
    if not isinstance(ctx, Context) or ctx.last_response is None:
        return
    try:
        evidence = _evidence(ctx.last_response)
    except Exception:
        return  # evita mascarar a falha original do teste com um erro na captura de evidência
    allure.attach(evidence, name=EVIDENCE_TITLE, attachment_type=allure.attachment_type.JSON)
    request.node.stash[EVIDENCE_KEY] = evidence


# A mesma evidência também aparece no terminal e no log do CI, junto da falha.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, Any, None]:
    outcome = yield
    report: pytest.TestReport = outcome.get_result()
    evidence = item.stash.get(EVIDENCE_KEY, None)
    if report.when == "call" and report.failed and evidence is not None:
        report.sections.append((EVIDENCE_TITLE, evidence))
