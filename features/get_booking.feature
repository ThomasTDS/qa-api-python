Feature: Consulta de booking

  @TC-004 @smoke
  Scenario: Buscar um booking existente pelo id
    Given que existe um booking criado
    When ele busca o booking pelo id
    Then os dados retornados devem corresponder ao booking criado

  @TC-005
  Scenario: Buscar um booking inexistente
    When ele busca o booking pelo id "999999999"
    Then a resposta deve indicar que o booking não foi encontrado

  @TC-006
  Scenario: Buscar bookings filtrando por firstname e lastname
    Given que existe um booking criado
    When ele busca bookings filtrando pelo firstname e lastname do booking criado
    Then o id do booking criado deve estar entre os resultados
    When ele busca bookings filtrando por um firstname e lastname que não correspondem a nenhum booking
    Then o id do booking criado não deve estar entre os resultados
