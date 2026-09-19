Feature: Autenticação na API restful-booker

  @TC-001 @smoke
  Scenario: Gerar token com credenciais válidas
    When ele solicita um token com o usuário "admin" e a senha "password123"
    Then ele deve receber um token de autenticação válido

  @TC-002
  Scenario: Tentar gerar token com credenciais inválidas
    When ele solicita um token com o usuário "admin" e a senha "senha_errada"
    Then a resposta deve indicar credenciais inválidas
