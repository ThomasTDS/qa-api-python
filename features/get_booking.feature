# language: pt
Funcionalidade: Consulta de booking

  @TC-004 @smoke
  Cenário: Buscar um booking existente pelo id
    Dado que existe um booking criado
    Quando o usuário busca o booking pelo id
    Então os dados retornados devem corresponder ao booking criado

  @TC-005
  Cenário: Buscar um booking inexistente
    Quando o usuário busca o booking pelo id "999999999"
    Então a resposta deve indicar que o booking não foi encontrado

  @TC-006
  Cenário: Buscar bookings filtrando por firstname e lastname
    Dado que existe um booking criado
    Quando o usuário busca bookings filtrando pelo firstname e lastname do booking criado
    Então o id do booking criado deve estar entre os resultados
    Quando o usuário busca bookings filtrando por um firstname e lastname que não correspondem a nenhum booking
    Então o id do booking criado não deve estar entre os resultados
