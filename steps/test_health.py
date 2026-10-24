from pytest_bdd import scenarios, then, when

from conftest import Context

scenarios("../features/health.feature")


@when("o usuário consulta o health check da API")
def consulta_o_health_check(context: Context) -> None:
    context.last_response = context.health_client.ping()


# A documentação da API define 201 Created como a resposta de sucesso do /ping.
@then("a API deve responder que está no ar")
def api_responde_que_esta_no_ar(context: Context) -> None:
    assert context.response.status_code == 201
