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

  # Comportamento observado na API pública: remover um id que nunca existiu
  # retorna 405 (Method Not Allowed), não 404 como seria de se esperar.
  # Documentado como comportamento real da API, não como bug da automação.
  @TC-014
  Scenario: Tentar remover um booking que não existe
    Given que ele possui um token de autenticação válido
    When ele tenta remover o booking pelo id "999999999"
    Then a resposta deve indicar que o método não é permitido
