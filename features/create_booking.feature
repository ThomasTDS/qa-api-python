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
