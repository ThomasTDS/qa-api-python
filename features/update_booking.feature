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

  # Diferente do TC-008 (token ausente): aqui o token existe, mas é inválido.
  # Validado manualmente que PATCH e DELETE se comportam da mesma forma (403),
  # então não repetimos esse caso pros outros dois verbos.
  @TC-013
  Scenario: Tentar atualizar booking com token inválido
    Given que existe um booking criado
    And que ele possui um token de autenticação inválido
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

  # PUT valida corretamente a ausência de campos obrigatórios (ao contrário
  # do POST de criação, que derruba com 500 no mesmo cenário — ver TC-015):
  # aqui a API responde com 400, como esperado.
  @TC-020
  Scenario: Tentar atualizar booking com corpo vazio
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele atualiza o booking com corpo vazio
    Then a resposta deve indicar requisição inválida

  # Mesmo defeito do TC-016 (totalprice de tipo inválido não é validado),
  # agora observado também no PUT: a API aceita e grava totalprice como
  # null em silêncio. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/22, que cobre os
  # dois verbos.
  @TC-021
  Scenario: Atualizar booking com totalprice em formato inválido
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele atualiza o booking com totalprice em formato inválido
    Then o booking deve ser atualizado com sucesso
    And o totalprice do booking atualizado deve ser nulo

  @TC-022
  Scenario: Tentar atualizar booking sem o campo bookingdates
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele atualiza o booking sem o campo bookingdates
    Then a resposta deve indicar requisição inválida

  # PATCH não valida o tipo de nenhum campo enviado: um lastname numérico é
  # aceito e gravado como número, quebrando o contrato do schema. Documentado
  # em https://github.com/ThomasTDS/qa-api-python/issues/23.
  @TC-023
  Scenario: Atualizar parcialmente o booking com lastname em formato inválido
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele atualiza parcialmente o booking com lastname em formato inválido
    Then o booking deve ser atualizado com sucesso
    And o lastname do booking atualizado deve ser o valor numérico enviado

  # Comportamento seguro, não um bug: PATCH com corpo vazio não falha nem
  # altera nada, documentado aqui como um no-op válido.
  @TC-024
  Scenario: Atualizar parcialmente o booking com corpo vazio não altera nada
    Given que existe um booking criado
    And que ele possui um token de autenticação válido
    When ele atualiza parcialmente o booking com corpo vazio
    Then o booking deve ser atualizado com sucesso
    And os dados do booking não devem ter sido alterados

  # Mesmo comportamento do TC-014 (DELETE em id inexistente retorna 405),
  # agora confirmado também em PUT e PATCH: nenhum dos três verbos retorna
  # 404 para um id que nunca existiu. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/24, que cobre os
  # três verbos.
  @TC-025
  Scenario Outline: Tentar atualizar um booking inexistente
    Given que ele possui um token de autenticação válido
    When ele tenta "<verbo>" um booking inexistente
    Then a resposta deve indicar que o método não é permitido

    Examples:
      | verbo                  |
      | atualizar              |
      | atualizar parcialmente |
