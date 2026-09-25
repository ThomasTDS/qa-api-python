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
| TC-009 | Atualização  | Atualizar parcialmente o booking com PATCH              | Funcional | Média      | Automatizado | [update_booking.feature:27](../features/update_booking.feature#L27)    |
| TC-010 | Remoção      | Remover booking com token válido                        | Funcional | Crítica    | Automatizado | [delete_booking.feature:3](../features/delete_booking.feature#L3)      |
| TC-011 | Remoção      | Tentar remover booking sem token de autenticação        | Negativo  | Alta       | Automatizado | [delete_booking.feature:9](../features/delete_booking.feature#L9)      |
| TC-012 | Atualização  | Tentar atualizar parcialmente booking sem token (PATCH) | Negativo  | Alta       | Automatizado | [update_booking.feature:36](../features/update_booking.feature#L36)    |
| TC-013 | Atualização  | Tentar atualizar booking com token inválido (PUT)       | Negativo  | Alta       | Automatizado | [update_booking.feature:17](../features/update_booking.feature#L17)    |
| TC-014 | Remoção      | Tentar remover um booking que não existe                | Negativo  | Baixa      | Automatizado | [delete_booking.feature:16](../features/delete_booking.feature#L16)    |
| TC-015 | Criação      | Tentar criar booking sem um campo obrigatório (bug)     | Negativo  | Média      | Automatizado | [create_booking.feature:13](../features/create_booking.feature#L13)    |
| TC-016 | Criação      | Criar booking com totalprice em formato inválido        | Negativo  | Média      | Automatizado | [create_booking.feature:24](../features/create_booking.feature#L24)    |
| TC-017 | Criação      | Criar booking com depositpaid em formato inválido       | Negativo  | Média      | Automatizado | [create_booking.feature:39](../features/create_booking.feature#L39)    |
| TC-018 | Criação      | Criar booking com checkin em formato inválido           | Negativo  | Média      | Automatizado | [create_booking.feature:49](../features/create_booking.feature#L49)    |
| TC-019 | Criação      | Criar booking com totalprice negativo                   | Negativo  | Baixa      | Automatizado | [create_booking.feature:58](../features/create_booking.feature#L58)    |
| TC-020 | Atualização  | Tentar atualizar booking com corpo vazio (PUT)          | Negativo  | Alta       | Automatizado | [update_booking.feature:47](../features/update_booking.feature#L47)    |
| TC-021 | Atualização  | Atualizar booking com totalprice em formato inválido    | Negativo  | Média      | Automatizado | [update_booking.feature:59](../features/update_booking.feature#L59)    |
| TC-022 | Atualização  | Tentar atualizar booking sem o campo bookingdates       | Negativo  | Alta       | Automatizado | [update_booking.feature:67](../features/update_booking.feature#L67)    |
| TC-023 | Atualização  | Atualizar parcialmente com lastname em formato inválido | Negativo  | Média      | Automatizado | [update_booking.feature:77](../features/update_booking.feature#L77)    |
| TC-024 | Atualização  | Atualizar parcialmente com corpo vazio não altera nada  | Funcional | Baixa      | Automatizado | [update_booking.feature:87](../features/update_booking.feature#L87)    |
| TC-025 | Atualização  | Tentar atualizar (PUT/PATCH) um booking inexistente     | Negativo  | Média      | Automatizado | [update_booking.feature:100](../features/update_booking.feature#L100)  |

`BookingApiClient.get_booking_ids` também aceita filtro por `checkin`/`checkout`, mas o TC-006 cobre só `firstname`/`lastname`: o filtro por data na API pública de demonstração é conhecido por ser instável, e testá-lo arriscaria um teste flaky em vez de validar um comportamento real.

TC-017 a TC-025 estendem a investigação de payload inválido (iniciada em TC-015/TC-016) para `depositpaid`, `checkin`, `totalprice` negativo e para os verbos PUT/PATCH: PUT valida corretamente campos obrigatórios ausentes (400), mas ainda corrompe silenciosamente um `totalprice` de tipo inválido — o mesmo defeito do TC-016, agora confirmado também nesse verbo; PATCH não valida tipo nenhum; e PUT/PATCH em um id inexistente retornam 405 Method Not Allowed, o mesmo comportamento já visto em DELETE (TC-014). Bugs reais novos (TC-017, TC-018, TC-019, TC-021+TC-016, TC-023, TC-025+TC-014) estão documentados como issues no GitHub.

## Smoke suite

Os fluxos ponta-a-ponta mais críticos (um caminho feliz por operação de CRUD, cobrindo autenticação + criação + consulta + atualização + remoção) estão marcados com a tag `@smoke` (marker `smoke` do pytest): **TC-001, TC-003, TC-004, TC-007, TC-010**.

Rodar apenas a smoke suite:

```
pytest -m smoke
```
