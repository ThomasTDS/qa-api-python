# language: pt
Funcionalidade: Remoção de booking

  @TC-010 @smoke
  Cenário: Remover booking com token válido
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário remove o booking
    Então o booking deve ser removido com sucesso

  @TC-011
  Cenário: Tentar remover booking sem token de autenticação
    Dado que existe um booking criado
    E que o usuário não possui nenhum token de autenticação
    Quando o usuário tenta remover o booking
    Então a resposta deve indicar acesso não autorizado

  # Comportamento observado na API pública: remover um id que nunca existiu
  # retorna 405 (Method Not Allowed), não 404 como seria de se esperar.
  # Documentado como comportamento real da API, não como bug da automação.
  @TC-014
  Cenário: Tentar remover um booking que não existe
    Dado que o usuário possui um token de autenticação válido
    Quando o usuário tenta remover o booking pelo id "999999999"
    Então a resposta deve indicar que o método não é permitido
