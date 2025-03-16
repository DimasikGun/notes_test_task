import pytest
from fastapi import status
from httpx import AsyncClient

from api.v1.auth.schemas import UserSchema
from api.v1.notes.schemas import CreateNoteSchema, UpdateNoteSchema

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


@pytest.mark.asyncio
async def test_create_note_ok(api_client: AsyncClient, mocker):
    mocker.patch(
        "api.v1.notes.helpers.create_note_summarization", return_value="Mocked summary"
    )

    note_data = CreateNoteSchema(title="Test Note", text="Test content")
    user_schema_in = UserSchema(
        username="user_create_note_ok", password="StrongTestPassword123!"
    )

    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    token = response.json()["access_token"]

    response = await api_client.post(
        f"{API_V1_PREFIX}/notes/",
        json=note_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["title"] == note_data.title
    assert data["text"] == note_data.text
    assert data["summarization"] == "Mocked summary"


@pytest.mark.asyncio
async def test_get_all_notes_ok(api_client: AsyncClient, mocker):
    mocker.patch(
        "api.v1.notes.helpers.create_note_summarization", return_value="Mocked summary"
    )

    user_schema_in = UserSchema(
        username="user_get_all_notes_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    token = data["access_token"]
    note_data_1 = CreateNoteSchema(title="Test Note 1", text="Content 1")
    await api_client.post(
        f"{API_V1_PREFIX}/notes/",
        json=note_data_1.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )
    note_data_2 = CreateNoteSchema(title="Test Note 2", text="Content 2")
    await api_client.post(
        f"{API_V1_PREFIX}/notes/",
        json=note_data_2.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    # Now, get all notes
    response = await api_client.get(
        f"{API_V1_PREFIX}/notes/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    assert data[0]["summarization"] == "Mocked summary"
    assert data[1]["summarization"] == "Mocked summary"


@pytest.mark.asyncio
async def test_get_single_note_ok(api_client: AsyncClient, mocker):
    mocker.patch(
        "api.v1.notes.helpers.create_note_summarization", return_value="Mocked summary"
    )
    note_data = CreateNoteSchema(title="Test Note", text="Test content")

    user_schema_in = UserSchema(
        username="user_get_single_note_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    token = data["access_token"]
    response = await api_client.post(
        f"{API_V1_PREFIX}/notes/",
        json=note_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    note_id = response.json()["id"]

    response = await api_client.get(
        f"{API_V1_PREFIX}/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == note_data.title
    assert data["text"] == note_data.text
    assert data["summarization"] == "Mocked summary"


@pytest.mark.asyncio
async def test_update_note_ok(api_client: AsyncClient, mocker):
    mocker.patch(
        "api.v1.notes.helpers.create_note_summarization",
        side_effect=["Mocked summary", "Updated mocked summary"],
    )
    user_schema_in = UserSchema(
        username="user_upd_note_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    token = data["access_token"]
    note_data = CreateNoteSchema(title="Test Note", text="Test content")

    # Create the note
    response = await api_client.post(
        f"{API_V1_PREFIX}/notes/",
        json=note_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["summarization"] == "Mocked summary"
    note_id = data["id"]

    # Update the note
    update_data = UpdateNoteSchema(title="Updated Note", text="Updated content")
    response = await api_client.patch(
        f"{API_V1_PREFIX}/notes/{note_id}",
        json=update_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == update_data.title
    assert data["text"] == update_data.text
    assert data["summarization"] == "Updated mocked summary"


@pytest.mark.asyncio
async def test_delete_note_ok(api_client: AsyncClient, mocker):
    mocker.patch(
        "api.v1.notes.helpers.create_note_summarization", return_value="Mocked summary"
    )
    note_data = CreateNoteSchema(title="Test Note", text="Test content")

    user_schema_in = UserSchema(
        username="user_del_note_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    token = data["access_token"]

    response = await api_client.post(
        f"{API_V1_PREFIX}/notes/",
        json=note_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    note_id = response.json()["id"]

    response = await api_client.delete(
        f"{API_V1_PREFIX}/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await api_client.get(
        f"{API_V1_PREFIX}/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_note_history_ok(api_client: AsyncClient, mocker):
    mocker.patch(
        "api.v1.notes.helpers.create_note_summarization",
        side_effect=["Mocked summary", "Updated mocked summary"],
    )
    note_data = CreateNoteSchema(title="Test Note", text="Test content")

    user_schema_in = UserSchema(
        username="user_get_note_with_history_ok", password="StrongTestPassword123!"
    )
    response = await api_client.post(
        f"{API_V1_PREFIX}{AUTH_PREFIX}/sign_up", json=user_schema_in.model_dump()
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    token = data["access_token"]

    response = await api_client.post(
        f"{API_V1_PREFIX}/notes/",
        json=note_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["summarization"] == "Mocked summary"
    note_id = data["id"]

    update_data = UpdateNoteSchema(title="Updated Note", text="Updated content")
    await api_client.patch(
        f"{API_V1_PREFIX}/notes/{note_id}",
        json=update_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await api_client.get(
        f"{API_V1_PREFIX}/notes/history/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["note_history"][0]["note_id"] == note_id
    assert data["summarization"] == "Updated mocked summary"
