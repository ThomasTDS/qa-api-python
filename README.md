# 🔌 QA API + pytest-bdd - restful-booker

[![API Tests](https://github.com/ThomasTDS/qa-api-python/actions/workflows/tests.yml/badge.svg)](https://github.com/ThomasTDS/qa-api-python/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/ThomasTDS/qa-api-python/branch/master/graph/badge.svg)](https://codecov.io/gh/ThomasTDS/qa-api-python)

## Descrição

Este repositório contém testes automatizados da API pública **[restful-booker](https://restful-booker.herokuapp.com)** utilizando **requests** (chamadas HTTP puras, sem navegador), **pytest-bdd (BDD/Gherkin)** e uma camada de **API Clients** que cumpre, para testes de API, o mesmo papel que o Page Object Model cumpre em testes de UI: encapsular as chamadas HTTP e esconder detalhes de endpoint/headers dos steps e dos cenários.

O objetivo é praticar testes de API "de verdade": autenticação, CRUD completo, diferença entre PUT e PATCH, e validação de regras de autorização.

---

## Estrutura do Projeto

```text
qa-api-python/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── bug_report.md   # Template de Issue para bugs reais
│   └── workflows/
│       └── tests.yml       # Pipeline de CI (push, PR e execução diária agendada)
├── docs/
│   └── test-cases.md       # Matriz de rastreabilidade dos test cases
├── features/                # Cenários em Gherkin (.feature)
├── steps/                   # Implementação dos steps do pytest-bdd (testes de integração, batem na API real)
├── tests/
│   └── unit/                # Testes unitários isolados de api/ e models/ (com requests-mock, sem rede)
├── api/                     # API Clients (AuthApiClient, BookingApiClient)
├── models/                  # Schemas Pydantic e tipos derivados (shape dos dados da API)
├── reports/                 # Relatório HTML e cobertura (coverage.xml) gerados a cada execução (não versionado)
├── conftest.py              # Fixtures (contexto por cenário) e captura de evidência de falha
├── pyproject.toml           # Dependências, scripts e configuração (pytest, ruff, mypy)
├── .pre-commit-config.yaml  # Hook de pre-commit (ruff)
├── LICENSE
└── README.md                # Este arquivo
```

---

### Instalar Dependências

```
python -m venv .venv
.venv\Scripts\activate       # PowerShell / Windows
source .venv/bin/activate    # bash / Linux / macOS

pip install -e ".[dev]"
pre-commit install
```

Não é necessário instalar nenhum navegador: como são testes de API, só a biblioteca `requests` é usada para fazer as chamadas HTTP.

### Rodar todos os testes

```
pytest
```

Ao final da execução, um relatório HTML é gerado em `reports/report.html` (não versionado).

O relatório da execução mais recente em `master` também fica publicado em **[thomastds.github.io/qa-api-python](https://thomastds.github.io/qa-api-python/)**, sem precisar rodar nada localmente ou baixar artifact do CI.

### Rodar apenas a smoke suite

```
pytest -m smoke
```

Roda só os fluxos ponta-a-ponta mais críticos (autenticação, criação, consulta, atualização e remoção — ver [docs/test-cases.md](docs/test-cases.md)). Como o `pyproject.toml` sempre escreve no mesmo arquivo, rodar isso depois de `pytest` **sobrescreve** `reports/report.html` com só esses 5 cenários.

### Rodar só os testes unitários

```
pytest tests/unit
```

Testes isolados de `api/` e `models/`, com as chamadas HTTP mocadas via [`requests-mock`](https://requests-mock.readthedocs.io/) — não fazem nenhuma chamada de rede, então rodam em milissegundos e não dependem da API pública estar no ar. Complementam os cenários de `steps/`, que são testes de integração de verdade contra a `restful-booker`.

### Lint e formatação

```
mypy .                    # typecheck
ruff check .              # lint
ruff format --check .     # formatação, só verifica
ruff format .             # formatação, aplica as correções
```

O CI roda `mypy`, `ruff check` e `ruff format --check` antes dos testes, então mudanças com problema de tipo ou estilo falham rápido, sem gastar tempo batendo na API pública.

Cada execução de `pytest` já gera cobertura de `api/` e `models/` (código dos API Clients e dos schemas), impressa no terminal e também em `reports/coverage.xml` (não versionado). No CI esse arquivo é enviado para o [Codecov](https://codecov.io/gh/ThomasTDS/qa-api-python), que mantém o histórico e mostra o badge no topo deste README.

Um hook de pre-commit (framework `pre-commit`, instalado via `pre-commit install` após o `pip install`) roda `ruff --fix` e `ruff format` nos arquivos staged antes de cada commit, então a maioria dos problemas de lint/formatação já é corrigida localmente antes de chegar no CI.

### Rodar contra outra URL

Por padrão os testes apontam para `https://restful-booker.herokuapp.com`. Para rodar contra outro ambiente (ex: uma instância local ou de staging), defina a variável de ambiente `BASE_URL`:

```
# PowerShell
$env:BASE_URL="http://localhost:3001"; pytest

# bash
BASE_URL=http://localhost:3001 pytest
```

---

### API testada

| Método | Rota           | Função                                             |
| ------ | -------------- | --------------------------------------------------- |
| POST   | `/auth`        | Gera token de autenticação                         |
| GET    | `/booking`     | Lista IDs de bookings (aceita filtros)             |
| GET    | `/booking/:id` | Busca um booking específico                        |
| POST   | `/booking`     | Cria um booking                                    |
| PUT    | `/booking/:id` | Atualiza um booking (todos os campos obrigatórios) |
| PATCH  | `/booking/:id` | Atualiza parcialmente um booking                   |
| DELETE | `/booking/:id` | Remove um booking                                  |

Autenticação: `POST /auth` com `{ "username": "admin", "password": "password123" }` retorna um token, enviado nas chamadas de `PUT`, `PATCH` e `DELETE` via cookie `token=<valor>`.

**Observação de segurança:** `POST /booking` (criação) **não exige autenticação** — qualquer pessoa consegue criar bookings sem token. Isso é uma falha de controle de acesso do próprio app de demonstração, e está coberta explicitamente em [features/create_booking.feature](features/create_booking.feature) como comportamento documentado, não como bug do teste.

---

### Estrutura de Testes e Padrões Aplicados

- BDD / Gherkin: cenários claros e legíveis em `.feature`, executados via `pytest-bdd`.
- API Client Objects: `AuthApiClient` e `BookingApiClient` encapsulam as chamadas HTTP, do mesmo jeito que Page Objects encapsulam elementos de UI.
- Pirâmide de testes: além dos cenários de BDD (`steps/`), que são testes de integração reais contra a `restful-booker`, `tests/unit/` cobre `api/` e `models/` de forma isolada, com `requests-mock` simulando as respostas HTTP — sem rede, sem depender da API pública estar no ar.
- Validação de schema com [Pydantic](https://docs.pydantic.dev/): as respostas da API são validadas em tempo de execução contra os modelos em `models/booking.py` (fonte única de verdade), não só tipadas por anotação — se a API mudar o formato de uma resposta, o teste falha com uma mensagem clara em vez de passar silenciosamente ou quebrar mais adiante.
- Cobertura de autenticação, CRUD completo, PUT vs. PATCH, e casos de acesso não autorizado (403).
- Relatório HTML automatizado a cada execução (`reports/report.html`, via `pytest-html`), com a versão da `master` publicada em [thomastds.github.io/qa-api-python](https://thomastds.github.io/qa-api-python/) via GitHub Pages.
- Cobertura de código (`pytest-cov`) de `api/` e `models/` em cada execução, acompanhada no [Codecov](https://codecov.io/gh/ThomasTDS/qa-api-python).
- Limpeza automática: a fixture `context` remove o booking criado no cenário (via token próprio de limpeza) ao final de cada teste, evitando acúmulo de dados na API pública.
- Retry automático (`pytest-rerunfailures`, `--reruns 1`): um cenário que falha roda uma segunda vez antes de ser reportado como falha, amortecendo instabilidade transitória da API pública de demonstração.
- Integração contínua via GitHub Actions: os testes rodam automaticamente a cada push e pull request para `master`, e também diariamente às 06:00 UTC (ver [.github/workflows/tests.yml](.github/workflows/tests.yml)) para detectar quebras causadas pela própria API pública, com o relatório HTML publicado como artifact do workflow.
- Dependências atualizadas automaticamente pelo Dependabot (pip e GitHub Actions, semanal — ver [.github/dependabot.yml](.github/dependabot.yml)). PRs de patch/minor com CI verde são mergeados automaticamente ([.github/workflows/dependabot-auto-merge.yml](.github/workflows/dependabot-auto-merge.yml)); bumps de major exigem revisão manual.
- Rastreabilidade de QA: matriz de test cases em [docs/test-cases.md](docs/test-cases.md), com tags `@TC-XXX` em cada `Scenario` e um subconjunto `@smoke` (`pytest -m smoke`) cobrindo os fluxos ponta-a-ponta mais críticos. Bugs reais encontrados são documentados como GitHub Issues usando o template em [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md).

---

### Fluxo de Trabalho

A branch `master` é protegida: toda mudança passa por Pull Request, e o merge só é liberado depois que o check de CI (`test`) passa. Fluxo padrão:

```
git checkout -b minha-branch
# editar, rodar pytest localmente
git push -u origin minha-branch
# abrir PR no GitHub, aguardar o check "test" passar, fazer merge
```
