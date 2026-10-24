# Estratégia de Testes

**Português** | [English](test-strategy.en.md)

Este documento explica o que é testado neste projeto, como e por quê. Cada decisão aponta para o arquivo que a implementa, para que dê para conferir no código.

## 1. Objetivo

Verificar o comportamento da API pública [restful-booker](https://restful-booker.herokuapp.com) (autenticação e CRUD de bookings) e documentar com evidência os defeitos encontrados. O projeto também serve de modelo de como organizar uma suíte de testes de API: legível, rastreável e confiável no CI.

## 2. Escopo

**Dentro do escopo:**

- Autenticação: geração de token com credenciais válidas e inválidas.
- Health check (`GET /ping`).
- CRUD de bookings: criação, consulta (por id, por filtro de nome e por filtro de datas de checkin e checkout), atualização completa (PUT), atualização parcial (PATCH) e remoção.
- Autorização: as duas formas de autenticação das operações de escrita (token no cookie e Basic auth), e chamadas sem credencial ou com credencial inválida.
- Validação de entrada: campos ausentes, tipos errados, valores negativos e datas em formato inválido.
- Contrato das respostas: formato e tipo de cada campo.

**Fora do escopo:**

- Testes de carga e desempenho: a API pública é compartilhada, e gerar carga nela prejudicaria outras pessoas.
- Interface web: a restful-booker não tem uma.
- Testes de intrusão: o projeto registra falhas de controle de acesso que aparecem nos testes funcionais, mas não ataca a API.

## 3. Abordagem por nível

| Nível | Onde | O que verifica | Por quê |
| ----- | ---- | -------------- | ------- |
| Estático | CI, job `unit` | Tipos (`mypy --strict`), estilo (`ruff`) e dependências vulneráveis (`pip-audit`) | Pega erros sem executar nada, em segundos |
| Unitário | [tests/unit/](../tests/unit/) | Se os API Clients montam cada requisição certo (URL, payload, cookie, timeout) e se os modelos aceitam e rejeitam o que devem | Roda sem rede, em milissegundos, e isola falhas do código do projeto das falhas da API |
| Integração (BDD) | [features/](../features/) e [steps/](../steps/) | O comportamento real da API, com cenários em Gherkin | Os cenários servem ao mesmo tempo de teste e de especificação legível |
| Contrato | [models/booking.py](../models/booking.py) | Cada resposta validada contra um modelo Pydantic no modo estrito | Uma mudança de formato ou de tipo na resposta falha o teste, em vez de passar sem ser notada |
| Smoke | tag `@smoke` | Os 5 fluxos mais críticos, de ponta a ponta | Uma verificação rápida de que o essencial funciona (`pytest -m smoke`) |
| Documentação | [tests/unit/test_traceability.py](../tests/unit/test_traceability.py) e [tests/unit/test_translation_sync.py](../tests/unit/test_translation_sync.py) | Se a matriz de test cases bate com os cenários e se as versões em português e inglês dos documentos têm a mesma estrutura | Documentação desatualizada é um defeito que nenhum teste funcional pega |

**Técnicas aplicadas:**

- **Partição de equivalência e valores inválidos:** para cada campo, um valor válido e as classes de valor inválido relevantes (ausente, tipo errado, negativo, formato errado).
- **Análise de valor-limite:** nos filtros por data, o booking é buscado com uma data anterior e com a mesma data do seu checkin, que é exatamente onde o filtro errado aparece (TC-027 e TC-028).
- **Testes negativos de autorização:** cada operação de escrita é testada sem token e com token inválido, e o Basic auth, com credenciais inválidas.
- **Testes de caracterização:** quando a API tem um bug, o cenário registra o comportamento atual e aponta para a issue que o documenta. Se a API for corrigida, o cenário falha, avisando que a issue pode ser fechada.

## 4. Ambientes

| Ambiente | Quando | Por quê |
| -------- | ------ | ------- |
| restful-booker local, num container ([docker-compose.yml](../docker-compose.yml)) | PRs e pushes na `master` | Resultado determinístico: mesma versão (fixada pelo digest da imagem) e mesmos dados iniciais a cada execução, sem depender do Heroku |
| API pública (Heroku) | Execução diária, às 06:00 UTC | Perceber quando o comportamento da API real mudar |
| Máquina de quem desenvolve | Sob demanda | Por padrão aponta para a API pública; com `docker compose up -d` e `BASE_URL=http://localhost:3001`, usa a local |

Os testes rodam em Python 3.12 e 3.13, com as dependências travadas no [uv.lock](../uv.lock).

## 5. Dados de teste

- Cada cenário cria os próprios dados a partir de um booking padrão ([steps/booking_data.py](../steps/booking_data.py)) e troca só o campo que interessa ao caso.
- O sobrenome ganha um sufixo aleatório, para que uma busca por nome encontre só o booking do próprio teste.
- Ao fim de cada teste, a fixture `context` ([conftest.py](../conftest.py)) remove o booking criado. Se a remoção falhar, um aviso mostra o id que ficou para trás.
- Nenhum cenário depende de dados criados por outro, então a ordem de execução não importa.

## 6. Critérios de entrada e saída

**Entrada:** os testes de integração só começam se o job `unit` passar (checagens estáticas e testes unitários) e se a API responder ao `GET /ping`.

**Saída, para mergear um PR**, configurada na proteção da branch `master`:

- `unit` e `integration` passando em Python 3.12 e 3.13.
- O código novo ou alterado em `api/` e `models/` 100% coberto (`codecov/patch`).
- Nenhuma vulnerabilidade conhecida nas dependências.
- A matriz de test cases e as traduções sincronizadas, verificadas pelos testes de documentação.

**Execução diária:** uma falha contra a API pública é investigada. Se for uma mudança de comportamento da API, ela vira uma issue ou atualiza uma existente, e o cenário é ajustado.

## 7. Riscos e mitigação

| Risco | Impacto | Mitigação |
| ----- | ------- | --------- |
| API pública fora do ar ou lenta | Falhas que não são do projeto, bloqueando o merge | API local nos PRs; timeout em toda chamada; retry só para falhas de rede |
| Dados alterados por terceiros na API pública | Resultado diferente a cada execução | API local nos PRs; dados únicos por teste; limpeza ao fim de cada teste |
| Mudança de contrato sem aviso | O teste passa com dados errados | Validação de schema no modo estrito; execução diária na API pública |
| Bug intermitente escondido pelo retry | Um defeito real passa na segunda tentativa | O retry só repete erros de conexão e de timeout, nunca falhas de asserção |
| Versão da API local diferente da pública | Um PR passa e a API real se comporta de outro jeito | Imagem fixada pelo digest; Dependabot avisa quando sai versão nova; a execução diária usa a pública |
| Dependência nova quebrando o CI ou com vulnerabilidade | CI vermelho sem mudança no projeto | Versões travadas no `uv.lock`; `pip-audit` em todo CI; Dependabot semanal |
| Documentação desatualizada | Matriz ou README descrevendo algo que não existe | Testes de rastreabilidade e de sincronia das traduções |
| Falha na execução diária sem ninguém perceber | Um problema fica dias sem tratamento (aconteceu entre 21 e 24/10/2026) | Planejado: abrir uma issue automaticamente quando a execução diária falhar |

## 8. Gestão de defeitos

- Cada defeito real da API vira uma issue no GitHub, com o [template de bug](../.github/ISSUE_TEMPLATE/bug_report.md): passos para reproduzir, resultado esperado e obtido, e evidência.
- O template separa **severidade** (impacto técnico: Blocker, Critical, Major, Minor) de **prioridade** (urgência de correção: P0 a P3), porque um defeito pode ser grave e pouco urgente, ou o contrário.
- O cenário que encontrou o defeito cita a issue num comentário no `.feature` e registra o comportamento atual (seção 3, testes de caracterização).
- Quando um teste falha no CI, o relatório mostra a URL, o status, os headers e o corpo da última resposta, o que já serve de evidência para a issue.

Até agora, 10 defeitos estão documentados: a maioria de validação de entrada ou de código de status, e dois de lógica nos filtros por data. Quando a causa pode ser confirmada no [código-fonte da API](https://github.com/mwinteringham/restful-booker), a issue aponta a linha responsável. Por exemplo: a API devolve 500 quando falta um campo obrigatório ([#8](https://github.com/ThomasTDS/qa-api-python/issues/8)) e aceita um preço negativo ([#21](https://github.com/ThomasTDS/qa-api-python/issues/21)).

## 9. Métricas e relatórios

- **Resultado de cada execução:** relatório HTML publicado no [GitHub Pages](https://thomastds.github.io/qa-api-python/) a cada push na `master`, e guardado como artifact em todo PR.
- **Cobertura de código:** de `api/` e `models/`, acompanhada no [Codecov](https://codecov.io/gh/ThomasTDS/qa-api-python).
- **Casos de teste:** 34 na [matriz](test-cases.md), sendo 15 funcionais e 19 negativos, com 3 de prioridade crítica.
- **Defeitos encontrados:** 10 issues abertas.
- **Tempo de execução:** a suíte completa roda em menos de 1 segundo contra a API local e em 25 a 40 segundos contra a pública.
