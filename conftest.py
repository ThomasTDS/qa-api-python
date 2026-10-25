import json
import os
import re
import warnings
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
import requests
from pydantic import ValidationError

from api.auth_api_client import AuthApiClient
from api.booking_api_client import BookingApiClient
from api.health_api_client import HealthApiClient
from models.booking import Booking

# Steps compartilhados entre features (token, Basic auth, booking criado, 403, 405 e 500).
pytest_plugins = ["steps.common_steps"]

BASE_URL = os.environ.get("BASE_URL", "https://restful-booker.herokuapp.com")
# O padrão são as credenciais públicas da documentação da restful-booker, para
# o projeto rodar sem configuração. Outro ambiente pode usar credenciais próprias.
API_USERNAME = os.environ.get("API_USERNAME", "admin")
API_PASSWORD = os.environ.get("API_PASSWORD", "password123")


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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, Any, None]:
    outcome = yield
    report: pytest.TestReport = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    ctx: Context | None = getattr(item, "funcargs", {}).get("context")
    if ctx is None or ctx.last_response is None:
        return

    try:
        response = ctx.last_response
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
        report.sections.append(("Evidência da falha", json.dumps(evidence, indent=2, ensure_ascii=False)))
    except Exception:
        pass  # evita mascarar a falha original do teste com um erro na captura de evidência
