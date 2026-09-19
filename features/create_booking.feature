Feature: Criação de booking

  # A documentação da API indica que POST /booking não exige autenticação.
  # Ou seja, qualquer pessoa consegue criar um booking sem token — uma falha
  # de controle de acesso do próprio app de demonstração, e vale documentar
  # esse comportamento em vez de presumir que a criação seria bloqueada.
  @TC-003 @smoke
  Scenario: Criar booking sem nenhum token de autenticação
    Given que ele não possui nenhum token de autenticação
    When ele cria um booking com dados válidos
    Then o booking deve ser criado com sucesso
    And o id do booking criado deve ser retornado

  # Bug real da API, documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/8: em vez de rejeitar
  # com 400, a API derruba com 500 quando falta um campo obrigatório. Esse
  # cenário trava o comportamento atual; se um dia passar a devolver 400,
  # é sinal de que o bug foi corrigido do lado de lá, e cabe atualizar o
  # teste (e fechar a issue).
  @TC-015
  Scenario: Tentar criar booking sem um campo obrigatório
    When ele tenta criar um booking sem informar o firstname
    Then a resposta deve indicar um erro interno do servidor

  # A API aceita um totalprice em formato errado (texto em vez de número) e
  # devolve 200, gravando null no lugar em silêncio, em vez de rejeitar o
  # payload. Esse cenário prova que a validação de schema do projeto pega
  # essa corrupção: a resposta não bate com o modelo Booking, e o teste
  # acusa o problema em vez de aceitar o dado corrompido como válido.
  @TC-016
  Scenario: Criar booking com totalprice em formato inválido
    When ele cria um booking com totalprice em formato inválido
    Then a resposta da API não deve corresponder ao schema esperado
