import pytest


@pytest.fixture()
def password() -> str:
    return "StrongTestPassword123!"


@pytest.fixture()
def payload() -> dict[str, str]:
    return {"sub": "user123"}
