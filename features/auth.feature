# language: pt
Funcionalidade: Autenticação na API restful-booker

  @TC-001 @smoke
  Cenário: Gerar token com credenciais válidas
    Quando o usuário solicita um token com credenciais válidas
    Então o usuário deve receber um token de autenticação válido

  @TC-002
  Cenário: Tentar gerar token com credenciais inválidas
    Quando o usuário solicita um token com o login "admin" e a senha "senha_errada"
    Então a resposta deve indicar credenciais inválidas
