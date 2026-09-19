# Matriz de Test Cases

Rastreabilidade dos casos de teste do projeto. Esta tabela **não duplica** os passos dos cenários — eles já estão documentados em Gherkin nos arquivos `.feature`, com o ID do test case como tag (`@TC-XXX`) em cada `Scenario`, garantindo rastreabilidade bidirecional.

Um `Scenario Outline` com `Examples` conta como um único test case (a variação de dados não infla a contagem).

Legenda:

- **Tipo**: `Funcional` (caminho feliz) ou `Negativo` (validação de erro/bloqueio esperado)
- **Prioridade**: importância do caso para o negócio (`Crítica` / `Alta` / `Média` / `Baixa`) — escala independente da Severidade/Prioridade usada nos [bug reports](../.github/ISSUE_TEMPLATE/bug_report.md), que mede urgência de correção de um defeito, não importância de um caso de teste
- **Automação**: `Automatizado` / `Manual` / `Planejado` (identificado, ainda não implementado)

| ID     | Módulo       | Título                                                  | Tipo      | Prioridade | Automação    | Cenário                                                               |
| ------ | ------------ | -------------------------------------------------------- | --------- | ---------- | ------------ | ---------------------------------------------------------------------- |
| TC-001 | Autenticação | Gerar token com credenciais válidas                     | Funcional | Crítica    | Automatizado | [auth.feature:3](../features/auth.feature#L3)                          |
| TC-002 | Autenticação | Tentar gerar token com credenciais inválidas            | Negativo  | Alta       | Automatizado | [auth.feature:7](../features/auth.feature#L7)                          |
| TC-003 | Criação      | Criar booking sem nenhum token de autenticação          | Funcional | Alta       | Automatizado | [create_booking.feature:7](../features/create_booking.feature#L7)      |
| TC-004 | Consulta     | Buscar um booking existente pelo id                     | Funcional | Alta       | Automatizado | [get_booking.feature:3](../features/get_booking.feature#L3)            |
| TC-005 | Consulta     | Buscar um booking inexistente                           | Negativo  | Média      | Automatizado | [get_booking.feature:8](../features/get_booking.feature#L8)            |
| TC-006 | Consulta     | Buscar bookings filtrando por firstname e lastname      | Funcional | Média      | Automatizado | [get_booking.feature:15](../features/get_booking.feature#L15)          |
| TC-007 | Atualização  | Atualizar booking com token válido (PUT)                | Funcional | Crítica    | Automatizado | [update_booking.feature:4](../features/update_booking.feature#L4)      |
| TC-008 | Atualização  | Tentar atualizar booking sem token de autenticação      | Negativo  | Alta       | Automatizado | [update_booking.feature:10](../features/update_booking.feature#L10)    |
| TC-009 | Atualização  | Atualizar parcialmente o booking com PATCH              | Funcional | Média      | Automatizado | [update_booking.feature:17](../features/update_booking.feature#L17)    |
| TC-010 | Remoção      | Remover booking com token válido                        | Funcional | Crítica    | Automatizado | [delete_booking.feature:3](../features/delete_booking.feature#L3)      |
| TC-011 | Remoção      | Tentar remover booking sem token de autenticação        | Negativo  | Alta       | Automatizado | [delete_booking.feature:9](../features/delete_booking.feature#L9)      |
| TC-012 | Atualização  | Tentar atualizar parcialmente booking sem token (PATCH) | Negativo  | Alta       | Automatizado | [update_booking.feature:27](../features/update_booking.feature#L27)    |

`BookingApiClient.get_booking_ids` também aceita filtro por `checkin`/`checkout`, mas o TC-006 cobre só `firstname`/`lastname`: o filtro por data na API pública de demonstração é conhecido por ser instável, e testá-lo arriscaria um teste flaky em vez de validar um comportamento real.

## Smoke suite

Os fluxos ponta-a-ponta mais críticos (um caminho feliz por operação de CRUD, cobrindo autenticação + criação + consulta + atualização + remoção) estão marcados com a tag `@smoke` (marker `smoke` do pytest): **TC-001, TC-003, TC-004, TC-007, TC-010**.

Rodar apenas a smoke suite:

```
pytest -m smoke
```
