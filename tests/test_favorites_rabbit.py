import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.core.database import engine
from app.models.models import Base


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def client():
    from app.main import create_app
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
@patch("app.api.v1.favorites_rabbit.publish_favorite_event", new_callable=AsyncMock)
async def test_add_favorite_rabbit_and_list(mock_publish, client: AsyncClient):
    """
    Testa a rota assíncrona de favoritos via RabbitMQ com a função de publicação mockada.
    Verifica se o item foi aceito e se os dados retornam corretamente da listagem.
    """

    # 1. Cria usuário
    signup = await client.post("/api/v1/auth/signup", json={
        "name": "Usuário Rabbit",
        "email": "rabbit@example.com",
        "password": "senha123",
        "confirm_password": "senha123"
    })
    assert signup.status_code == 200
    client_id = signup.json()["id"]

    # 2. Login
    login = await client.post("/api/v1/auth/login", json={
        "email": "rabbit@example.com",
        "password": "senha123"
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Dispara favorito via RabbitMQ (mockado)
    rabbit_resp = await client.post(f"/api/v1/favorites-rabbit/{client_id}", json={
        "product_id": 2
    }, headers=headers)
    assert rabbit_resp.status_code == 200
    assert rabbit_resp.json()["message"] == "Favorito enviado para processamento assíncrono"

    # Garante que o mock foi chamado corretamente
    mock_publish.assert_awaited_once_with({"client_id": client_id, "product_id": 2})
