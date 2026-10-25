# language: pt
Funcionalidade: Segurança da API

  # Testes de segurança leves, baseados no OWASP API Security Top 10. Cada
  # cenário faz poucas requisições: nada de carga, força bruta ou qualquer
  # coisa que prejudique a API pública. Os cenários de falha registram o
  # comportamento atual e apontam a issue; os de proteção garantem que uma
  # defesa que funciona hoje não suma numa versão nova da API.

  # Os filtros de nome copiam o parâmetro da URL direto para a consulta ao
  # banco, então "lastname[$ne]=x" vira a condição "sobrenome diferente de x"
  # e traz bookings que não deveriam aparecer. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/64.
  @TC-035 @seguranca
  Cenário: Injeção NoSQL no filtro de busca traz bookings de outro sobrenome
    Dado que existe um booking criado
    Quando o usuário busca bookings com um operador do banco no filtro de lastname
    Então o booking criado deve aparecer mesmo sem ter o sobrenome buscado

  # Proteção que funciona: o login compara usuário e senha com igualdade
  # estrita, então um operador do banco no lugar da senha não autentica.
  @TC-036 @seguranca
  Cenário: Login recusa um operador do banco no lugar da senha
    Quando o usuário tenta fazer login com um operador do banco no lugar da senha
    Então o login deve ser recusado

  # A API revela que usa Express e não envia cabeçalhos básicos de proteção
  # de navegador. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/65.
  @TC-037 @seguranca
  Cenário: Respostas expõem a tecnologia do servidor e não trazem cabeçalhos de segurança
    Quando o usuário consulta o health check da API
    Então a resposta deve expor a tecnologia do servidor no cabeçalho X-Powered-By
    E a resposta não deve trazer os cabeçalhos X-Content-Type-Options e X-Frame-Options

  # Proteção que funciona: o script é gravado como texto e devolvido numa
  # resposta JSON, que o navegador não executa.
  @TC-038 @seguranca
  Cenário: Script num campo de texto volta como texto, numa resposta JSON
    Quando o usuário cria um booking com um script no firstname
    E o usuário consulta esse booking
    Então a resposta deve ser JSON, e não HTML
    E o firstname deve voltar exatamente como foi enviado

  # Proteção que funciona: um erro devolve uma mensagem genérica, sem rastro
  # de pilha nem detalhes internos do servidor.
  @TC-039 @seguranca
  Cenário: Erro de requisição não expõe detalhes internos
    Quando o usuário cria um booking com um corpo que não é JSON válido
    Então a resposta deve ser um erro genérico, sem detalhes internos

  # Proteção que funciona: a API gera o próprio id, e um bookingid enviado
  # no corpo é ignorado (sem atribuição em massa).
  @TC-040 @seguranca
  Cenário: Bookingid enviado no corpo da criação é ignorado
    Quando o usuário cria um booking informando o próprio bookingid
    Então a API deve ignorar o bookingid enviado

  # Os tokens ficam guardados em memória para sempre: um token antigo continua
  # valendo depois de um login novo. Documentado em
  # https://github.com/ThomasTDS/qa-api-python/issues/66.
  @TC-041 @seguranca
  Cenário: Token antigo continua válido depois de um novo login
    Dado que existe um booking criado
    E que o usuário possui um token de autenticação válido
    E que o usuário faz um novo login
    Quando o usuário atualiza parcialmente o booking com o token anterior
    Então o token anterior ainda deve ser aceito
