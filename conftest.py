import json
import os
from collections.abc import Generator
from typing import Any

import pytest
import requests

from api.auth_api_client import AuthApiClient
from api.booking_api_client import BookingApiClient
from models.booking import Booking

BASE_URL = os.environ.get("BASE_URL", "https://restful-booker.herokuapp.com")


class Context:
    def __init__(self, session: requests.Session) -> None:
        self.session = session
        self.auth_client = AuthApiClient(session, BASE_URL)
        self.booking_client = BookingApiClient(session, BASE_URL)
        self.token: str | None = None
        self.booking_id: int | None = None
        self.booking_data: Booking | None = None
        self.last_response: requests.Response | None = None


@pytest.fixture
def context() -> Generator[Context, None, None]:
    session = requests.Session()
    ctx = Context(session)
    yield ctx

    if ctx.booking_id is not None:
        try:
            cleanup_token = ctx.auth_client.get_valid_token()
            ctx.booking_client.delete_booking(ctx.booking_id, cleanup_token)
        except Exception:
            pass  # booking já pode ter sido removido pelo próprio cenário; ignora falha de limpeza

    session.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, Any, None]:
    outcome = yield
    report: pytest.TestReport = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    ctx: Context | None = getattr(item, "funcargs", {}).get("context")
    if ctx is None or ctx.last_response is None:
        return

    try:
        response = ctx.last_response
        try:
            body = response.json()
        except ValueError:
            body = response.text
        evidence = {
            "url": response.url,
            "status": response.status_code,
            "reason": response.reason,
            "headers": dict(response.headers),
            "body": body,
        }
        report.sections.append(("Evidência da falha", json.dumps(evidence, indent=2, ensure_ascii=False)))
    except Exception:
        pass  # evita mascarar a falha original do teste com um erro na captura de evidência
