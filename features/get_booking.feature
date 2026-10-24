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

  @TC-027
  Cenário: Buscar bookings com checkin a partir de uma data anterior à do booking
    Dado que existe um booking criado com checkin em "2026-01-10" e checkout em "2026-01-15"
    Quando o usuário busca o booking criado com o filtro de checkin "2026-01-09"
    Então o id do booking criado deve estar entre os resultados

  # A documentação diz que o filtro checkin traz bookings com checkin "maior
  # ou igual" à data informada, mas a API usa "maior que": um booking com
  # checkin exatamente na data do filtro fica de fora. Defeito de valor-limite,
  # com a causa confirmada no código da API, documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/54.
  @TC-028
  Cenário: Buscar bookings com checkin a partir da mesma data do booking
    Dado que existe um booking criado com checkin em "2026-01-10" e checkout em "2026-01-15"
    Quando o usuário busca o booking criado com o filtro de checkin "2026-01-10"
    Então o id do booking criado não deve estar entre os resultados

  # Pela documentação, o filtro checkout também é "maior ou igual", então um
  # checkout posterior ao do booking deveria deixá-lo de fora. A API faz o
  # contrário e traz bookings com checkout até a data informada. Documentado
  # em https://github.com/ThomasTDS/qa-api-python/issues/55.
  @TC-029
  Cenário: Buscar bookings com checkout a partir de uma data posterior à do booking
    Dado que existe um booking criado com checkin em "2026-01-10" e checkout em "2026-01-15"
    Quando o usuário busca o booking criado com o filtro de checkout "2026-01-16"
    Então o id do booking criado deve estar entre os resultados

  # Mesmo padrão do TC-015: em vez de rejeitar a data inválida com 400, a API
  # derruba com 500. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/56.
  @TC-030
  Cenário: Tentar buscar bookings com uma data inválida no filtro
    Quando o usuário busca bookings com o filtro de checkin "data-invalida"
    Então a resposta deve indicar um erro interno do servidor
