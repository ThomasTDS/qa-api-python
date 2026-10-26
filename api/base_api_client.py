from typing import Any

import requests

# (conexão, resposta), em segundos. A conexão falha rápido se o servidor nem
# responde; a resposta tem margem para o Heroku acordar a aplicação, que pode
# demorar na primeira chamada depois de um tempo parada.
DEFAULT_TIMEOUT = (5, 30)


class BaseApiClient:
    def __init__(
        self,
        session: requests.Session,
        base_url: str,
        timeout: tuple[float, float] = DEFAULT_TIMEOUT,
    ) -> None:
        self.session = session
        self.base_url = base_url
        self.timeout = timeout

    # Nos clients, o método HTTP fica numa linha própria, marcada com
    # "# pragma: no mutate": o requests converte o método para maiúsculas, então
    # a mutação "GET" -> "get" do teste de mutação é equivalente e nenhum
    # teste conseguiria percebê-la. O caminho, na linha seguinte, continua sendo
    # mutado. Pelo mesmo motivo, o nome de cabeçalho "Content-Type" também é
    # marcado: cabeçalhos HTTP não diferenciam maiúsculas de minúsculas.
    #
    # Ponto único por onde passam todas as chamadas HTTP dos clients, para
    # que nenhuma requisição fique sem timeout (o requests não tem um padrão
    # e, sem ele, pode esperar uma resposta para sempre).
    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        return self.session.request(method, f"{self.base_url}{path}", timeout=self.timeout, **kwargs)
