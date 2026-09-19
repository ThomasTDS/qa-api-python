Feature: Remoção de booking

  @TC-010 @smoke
  Scenario: Remover booking com token válido
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele remove o booking
    Then o booking deve ser removido com sucesso

  @TC-011
  Scenario: Tentar remover booking sem token de autenticação
    Given que existe um booking criado
    And que ele não possui nenhum token de autenticação
    When ele tenta remover o booking
    Then a resposta deve indicar acesso não autorizado
