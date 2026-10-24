# language: pt
Funcionalidade: Verificação de saúde da API

  # A documentação da API define o /ping como health check, com 201 Created
  # como resposta de sucesso. É um código incomum para uma consulta (o usual
  # seria 200), mas é o comportamento documentado, não um defeito.
  @TC-026
  Cenário: Verificar que a API está no ar
    Quando o usuário consulta o health check da API
    Então a API deve responder que está no ar
