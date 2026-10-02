# language: pt
Funcionalidade: Atualização de booking (PUT e PATCH)

  # PUT substitui todos os campos do booking; exige todos os campos obrigatórios.
  @TC-007 @smoke
  Cenário: Atualizar booking com token válido
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário atualiza o booking com novos dados
    Então o booking deve ser atualizado com sucesso

  @TC-008
  Cenário: Tentar atualizar booking sem token de autenticação
    Dado que existe um booking criado
    E que o usuário não possui nenhum token de autenticação
    Quando o usuário tenta atualizar o booking com novos dados
    Então a resposta deve indicar acesso não autorizado

  # Diferente do TC-008 (token ausente): aqui o token existe, mas é inválido.
  # Validado manualmente que PATCH e DELETE se comportam da mesma forma (403),
  # então não repetimos esse caso pros outros dois verbos.
  @TC-013
  Cenário: Tentar atualizar booking com token inválido
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação inválido
    Quando o usuário tenta atualizar o booking com novos dados
    Então a resposta deve indicar acesso não autorizado

  # PATCH atualiza somente os campos enviados, mantendo o restante do booking.
  @TC-009
  Cenário: Atualizar parcialmente o booking com PATCH
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário atualiza parcialmente o booking alterando o sobrenome para "Silva"
    Então o booking deve ser atualizado com sucesso
    E o sobrenome do booking deve ser "Silva"

  @TC-012
  Cenário: Tentar atualizar parcialmente booking sem token de autenticação
    Dado que existe um booking criado
    E que o usuário não possui nenhum token de autenticação
    Quando o usuário tenta atualizar parcialmente o booking alterando o sobrenome para "NaoDeveriaFuncionar"
    Então a resposta deve indicar acesso não autorizado

  # PUT valida corretamente a ausência de campos obrigatórios (ao contrário
  # do POST de criação, que derruba com 500 no mesmo cenário — ver TC-015):
  # aqui a API responde com 400, como esperado.
  @TC-020
  Cenário: Tentar atualizar booking com corpo vazio
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário atualiza o booking com corpo vazio
    Então a resposta deve indicar requisição inválida

  # Mesmo defeito do TC-016 (totalprice de tipo inválido não é validado),
  # agora observado também no PUT: a API aceita e grava totalprice como
  # null em silêncio. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/22, que cobre os
  # dois verbos.
  @TC-021
  Cenário: Atualizar booking com totalprice em formato inválido
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário atualiza o booking com totalprice em formato inválido
    Então o booking deve ser atualizado com sucesso
    E o totalprice do booking atualizado deve ser nulo

  @TC-022
  Cenário: Tentar atualizar booking sem o campo bookingdates
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário atualiza o booking sem o campo bookingdates
    Então a resposta deve indicar requisição inválida

  # PATCH não valida o tipo de nenhum campo enviado: um lastname numérico é
  # aceito e gravado como número, quebrando o contrato do schema. Documentado
  # em https://github.com/ThomasTDS/qa-api-python/issues/23.
  @TC-023
  Cenário: Atualizar parcialmente o booking com lastname em formato inválido
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário atualiza parcialmente o booking com lastname em formato inválido
    Então o booking deve ser atualizado com sucesso
    E o lastname do booking atualizado deve ser o valor numérico enviado

  # Comportamento seguro, não um bug: PATCH com corpo vazio não falha nem
  # altera nada, documentado aqui como um no-op válido.
  @TC-024
  Cenário: Atualizar parcialmente o booking com corpo vazio não altera nada
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    Quando o usuário atualiza parcialmente o booking com corpo vazio
    Então o booking deve ser atualizado com sucesso
    E os dados do booking não devem ter sido alterados

  # Mesmo comportamento do TC-014 (DELETE em id inexistente retorna 405),
  # agora confirmado também em PUT e PATCH: nenhum dos três verbos retorna
  # 404 para um id que nunca existiu. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/24, que cobre os
  # três verbos.
  @TC-025
  Esquema do Cenário: Tentar atualizar um booking inexistente
    Dado que o usuário possui um token de autenticação válido
    Quando o usuário tenta "<verbo>" um booking inexistente
    Então a resposta deve indicar que o método não é permitido

    Exemplos:
      | verbo                  |
      | atualizar              |
      | atualizar parcialmente |
