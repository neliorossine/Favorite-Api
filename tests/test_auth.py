import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import create_app
from app.core.database import Base, engine

app = create_app()

@pytest_asyncio.fixture(scope="function")
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@pytest_asyncio.fixture(scope="function")
async def client(prepare_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register_user_success(client):
    response = await client.post("/api/v1/auth/signup", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
        "confirm_password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "Usuário criado com sucesso"
    assert data["email"] == "testuser@example.com"

@pytest.mark.asyncio
async def test_login_user_success(client):
    # Cria o usuário antes de logar
    await client.post("/api/v1/auth/signup", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
        "confirm_password": "testpassword"
    })

    response = await client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    # Cria o usuário antes de tentar login inválido
    await client.post("/api/v1/auth/signup", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
        "confirm_password": "testpassword"
    })

    response = await client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"
