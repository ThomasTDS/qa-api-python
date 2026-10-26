# Test Strategy

[Português](test-strategy.md) | **English**

This document explains what this project tests, how, and why. Each decision points to the file that implements it, so it can be checked against the code. The Gherkin scenarios and the test case matrix it refers to are written in Portuguese.

## 1. Objective

Verify the behavior of the public [restful-booker](https://restful-booker.herokuapp.com) API (authentication and booking CRUD) and document the defects found, with evidence. The project is also an example of how to organize an API test suite: readable, traceable and reliable in CI.

## 2. Scope

**In scope:**

- Authentication: token creation with valid and invalid credentials.
- Health check (`GET /ping`).
- Booking CRUD: creation, retrieval (by id, by name filter and by checkin and checkout date filters), full update (PUT), partial update (PATCH) and deletion.
- Authorization: both authentication methods for write operations (token in a cookie and Basic auth), and calls with no credentials or with invalid ones.
- Input validation: missing fields, wrong types, negative values and dates in an invalid format.
- Response contract: shape and type of every field.
- Response time: every response within a limit, without generating load.
- Security, based on the OWASP API Security Top 10: NoSQL injection, security headers, internal details in error responses, mass assignment and token validity.

**Out of scope:**

- Load and stress testing: the public API is shared, and generating load on it would hurt other people. The project only checks the time of each response, on the requests the scenarios already make.
- Web interface: restful-booker does not have one.
- Full penetration testing, brute force and automated scanning: the project's security tests are light, with few requests each, so as not to harm the public API.

## 3. Approach by level

| Level | Where | What it checks | Why |
| ----- | ----- | -------------- | --- |
| Static | CI, `unit` job | Types (`mypy --strict`), style (`ruff`) and vulnerable dependencies (`pip-audit`) | Catches errors without running anything, in seconds |
| Unit | [tests/unit/](../tests/unit/) | Whether the API Clients build each request correctly (URL, payload, cookie, timeout) and whether the models accept and reject what they should | Runs with no network, in milliseconds, and separates failures in the project's code from failures in the API |
| Integration (BDD) | [features/](../features/) and [steps/](../steps/) | The real behavior of the API, with Gherkin scenarios | The scenarios work as tests and as a readable specification at the same time |
| Contract | [models/booking.py](../models/booking.py) | Each response validated against a Pydantic model in strict mode | A change in the shape or type of a response fails the test instead of going unnoticed |
| Properties | [tests/unit/test_properties.py](../tests/unit/test_properties.py) | Rules that hold for any input: JSON round trip, rejection of wrong types, filters sent by the search | Hypothesis generates hundreds of inputs (1000 per test in CI) and finds cases nobody would write by hand, such as `NaN` in the price and the text `"0"` accepted as a date |
| Mutation | [.github/workflows/mutation.yml](../.github/workflows/mutation.yml), weekly | Whether the unit tests notice deliberate changes to the code in `api/` and `models/` | Coverage says a line ran, not that any test would fail if it were wrong; mutmut measures that |
| Smoke | `@smoke` tag | The 5 most critical end-to-end flows | A quick check that the essentials work (`pytest -m smoke`) |
| Security | [features/security.feature](../features/security.feature), `@seguranca` tag | Injection, headers, errors, mass assignment and session | Security flaws slip past functional tests; the protection scenarios make sure a defense does not disappear in a new version (`pytest -m seguranca`) |
| Performance | Every request made by the scenarios ([conftest.py](../conftest.py)) | Whether each response arrives within the limit (`RESPONSE_TIME_LIMIT_MS`): 500 ms on the local API and 3 s on the public one | Catches performance regressions without generating any load, since it reuses the requests the scenarios already make |
| Documentation | [tests/unit/test_traceability.py](../tests/unit/test_traceability.py) and [tests/unit/test_translation_sync.py](../tests/unit/test_translation_sync.py) | Whether the test case matrix matches the scenarios and whether the Portuguese and English versions of the documents have the same structure | Outdated documentation is a defect that no functional test catches |

**Techniques applied:**

- **Equivalence partitioning and invalid values:** for each field, one valid value and the relevant classes of invalid values (missing, wrong type, negative, wrong format).
- **Boundary value analysis:** in the date filters, the booking is searched with a date before its checkin and with the same date, which is exactly where the faulty filter shows up (TC-027 and TC-028).
- **Negative authorization tests:** every write operation is tested with no token and with an invalid token, and Basic auth with invalid credentials.
- **Property-based testing:** instead of examples, a rule that must hold for any input, tested by Hypothesis with generated values. When it finds a case that breaks the rule, the case becomes a fixed example in the test, so it is always checked.
- **Characterization tests:** when the API has a bug, the scenario records the current behavior and points to the issue that documents it. If the API gets fixed, the scenario fails, signaling that the issue can be closed.

## 4. Environments

| Environment | When | Why |
| ----------- | ---- | --- |
| Local restful-booker in a container ([docker-compose.yml](../docker-compose.yml)) | PRs and pushes to `master` | Deterministic results: same version (pinned by the image digest) and same initial data on every run, with no dependency on Heroku |
| Public API (Heroku) | Daily run, at 06:00 UTC | Catch changes in the real API's behavior |
| Developer machine | On demand | Targets the public API by default; with `docker compose up -d` and `BASE_URL=http://localhost:3001`, it uses the local one |

The tests run on Python 3.12 and 3.13, with dependencies locked in [uv.lock](../uv.lock).

## 5. Test data

- Each scenario creates its own data from a default booking ([steps/booking_data.py](../steps/booking_data.py)) and changes only the field relevant to the case.
- The last name gets a random suffix, so a search by name finds only the test's own booking.
- At the end of each test, the `context` fixture ([conftest.py](../conftest.py)) deletes the booking it created. If the deletion fails, a warning shows the id left behind.
- No scenario depends on data created by another, so execution order does not matter. The daily run proves it: against the public API, the scenarios run in 4 parallel processes (`pytest-xdist`).

## 6. Entry and exit criteria

**Entry:** the integration tests only start if the `unit` job passes (static checks and unit tests) and if the API answers `GET /ping`. This check runs once per execution, through the `api_disponivel` fixture ([conftest.py](../conftest.py)): with no answer, each integration test shows up as an error with the reason, and the unit tests run normally.

**Exit, to merge a PR**, configured in the `master` branch protection:

- `unit` and `integration` passing on Python 3.12 and 3.13.
- New or changed code in `api/` and `models/` 100% covered (`codecov/patch`).
- No known vulnerability in the dependencies.
- The test case matrix and the translations in sync, checked by the documentation tests.

**Daily run:** a failure against the public API automatically opens an issue with the `execucao-diaria` label, assigned to the repository owner; if it is already open, the new failure becomes a comment. The issue closes on its own at the first daily run that passes again. Each failure gets investigated. If it is a change in the API's behavior, it becomes an issue or updates an existing one, and the scenario is adjusted.

## 7. Risks and mitigation

| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |
| Public API down or slow | Failures that are not the project's fault, blocking the merge | Local API on PRs; health check that stops the integration tests with a clear message; timeout on every call; retry for network failures only |
| Data changed by third parties on the public API | Different results on every run | Local API on PRs; unique data per test; cleanup at the end of each test |
| Contract change without notice | The test passes with wrong data | Schema validation in strict mode; daily run against the public API |
| Intermittent bug hidden by the retry | A real defect passes on the second attempt | The retry only repeats connection and timeout errors, never assertion failures |
| Performance regression | The API gets slow and no test fails, because the result is still correct | Time limit on every scenario response: 500 ms on the local API and 3 s on the public one (twice the worst time measured, about 1.4 s) |
| Local API version different from the public one | A PR passes and the real API behaves differently | Image pinned by digest; Dependabot flags new versions; the daily run uses the public API |
| New dependency breaking CI or carrying a vulnerability | Red CI with no change in the project | Versions locked in `uv.lock`; `pip-audit` on every CI run; weekly Dependabot |
| Outdated documentation | Matrix or README describing something that does not exist | Traceability and translation sync tests |
| Daily run failing without anyone noticing | A problem goes untreated for days (it happened from Oct 21 to 24, 2026) | A daily run failure opens an issue automatically, and it closes on its own when the run passes again |

## 8. Defect management

- Each real defect in the API becomes a GitHub issue, using the [bug template](../.github/ISSUE_TEMPLATE/bug_report.md): steps to reproduce, expected and actual result, and evidence.
- The template separates **severity** (technical impact: Blocker, Critical, Major, Minor) from **priority** (urgency to fix: P0 to P3), because a defect can be serious and not urgent, or the other way around.
- The scenario that found the defect cites the issue in a comment in the `.feature` file and records the current behavior (section 3, characterization tests).
- When a scenario fails, the URL, status, headers and body of the last response are attached to the failing step in the Allure report, and also show up in the terminal and the CI log. That already serves as evidence for the issue.

So far, 13 defects are documented: most about input validation or status codes, two about logic in the date filters and three about security. When the cause can be confirmed in the [API source code](https://github.com/mwinteringham/restful-booker), the issue points to the line responsible. For example: the API returns 500 when a required field is missing ([#8](https://github.com/ThomasTDS/qa-api-python/issues/8)) and accepts a negative price ([#21](https://github.com/ThomasTDS/qa-api-python/issues/21)).

## 9. Metrics and reports

- **Result of each run:** Allure report published on [GitHub Pages](https://thomastds.github.io/qa-api-python/) on every push to `master`, with the history across runs (trends and flaky tests), and kept as an artifact on every PR. Allure shows the BDD scenarios; the unit test results stay in the CI log.
- **Code coverage:** of `api/` and `models/`, tracked on [Codecov](https://codecov.io/gh/ThomasTDS/qa-api-python).
- **Mutation score:** 93% (200 of 215 mutants killed), measured every week. The 15 survivors are equivalent (HTTP method and header name, which are case-insensitive).
- **Test cases:** 41 in the [matrix](test-cases.md), 15 functional and 26 negative, with 4 of critical priority.
- **Defects found:** 13 open issues.
- **Run time:** the full suite runs in under 1 second against the local API and in 25 to 40 seconds against the public one.
