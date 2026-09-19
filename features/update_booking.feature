Feature: Atualização de booking (PUT e PATCH)

  # PUT substitui todos os campos do booking; exige todos os campos obrigatórios.
  @TC-007 @smoke
  Scenario: Atualizar booking com token válido
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele atualiza o booking com novos dados
    Then o booking deve ser atualizado com sucesso

  @TC-008
  Scenario: Tentar atualizar booking sem token de autenticação
    Given que existe um booking criado
    And que ele não possui nenhum token de autenticação
    When ele tenta atualizar o booking com novos dados
    Then a resposta deve indicar acesso não autorizado

  # PATCH atualiza somente os campos enviados, mantendo o restante do booking.
  @TC-009
  Scenario: Atualizar parcialmente o booking com PATCH
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele atualiza parcialmente o booking alterando o sobrenome para "Silva"
    Then o booking deve ser atualizado com sucesso
    And o sobrenome do booking deve ser "Silva"

  @TC-012
  Scenario: Tentar atualizar parcialmente booking sem token de autenticação
    Given que existe um booking criado
    And que ele não possui nenhum token de autenticação
    When ele tenta atualizar parcialmente o booking alterando o sobrenome para "NaoDeveriaFuncionar"
    Then a resposta deve indicar acesso não autorizado
