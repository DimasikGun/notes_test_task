import pytest
from fastapi import status
from httpx import AsyncClient

from api.v1.auth.schemas import UserSchema

API_V1_PREFIX = "/api/v1"
AUTH_PREFIX = "/auth"


@pytest.mark.asyncio
async def test_sign_up_ok(api_client: AsyncClient, user_schema_in: UserSchema):
    user_schema_in = UserSchema(
        username="user_sign_up_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_sign_up_failed(api_client: AsyncClient, user_dict_in_weak_pass: dict):
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up",
        json=user_dict_in_weak_pass,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_ok(api_client: AsyncClient):
    user_schema_in = UserSchema(
        username="user_login_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/login", json=user_schema_in.model_dump()
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_login_failed(api_client: AsyncClient, user_schema_in):
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/login", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_info_ok(api_client: AsyncClient):
    user_schema_in = UserSchema(
        username="user_me_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    token = data["access_token"]
    response = await api_client.get(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == user_schema_in.username


@pytest.mark.asyncio
async def test_get_user_info_unauthorized(api_client: AsyncClient):
    response = await api_client.get(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_ok(api_client: AsyncClient):
    user_schema_in = UserSchema(
        username="user_refresh_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    token = data["refresh_token"]
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_refresh_failed(api_client: AsyncClient):
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/refresh",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
