from pytest_bdd import scenarios, then

from conftest import Context

scenarios("../features/health.feature")


# A documentação da API define 201 Created como a resposta de sucesso do /ping.
@then("a API deve responder que está no ar")
def api_responde_que_esta_no_ar(context: Context) -> None:
    assert context.response.status_code == 201
