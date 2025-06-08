import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.core.database import engine
from app.models.models import Base


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_test_db():
    """
    Executa a criação e limpeza do banco antes de cada teste.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Retorna um cliente HTTP assíncrono para testes com o app FastAPI.
    """
    from app.main import create_app
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_add_and_list_favorites(client: AsyncClient):
    """
    Teste completo para adicionar e listar produtos favoritos de um cliente autenticado.
    """

    # 1. Cadastro do cliente
    signup_resp = await client.post("/api/v1/auth/signup", json={
        "name": "Usuário de Teste",
        "email": "teste@example.com",
        "password": "senha123",
        "confirm_password": "senha123"
    })
    assert signup_resp.status_code == 200
    client_id = signup_resp.json()["id"]

    # 2. Login e obtenção do token JWT
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "teste@example.com",
        "password": "senha123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Adiciona um produto aos favoritos
    add_resp = await client.post(f"/api/v1/favorites/{client_id}", json={
        "product_id": 1
    }, headers=headers)
    assert add_resp.status_code == 200
    response_data = add_resp.json()
    assert response_data["product_id"] == 1
    assert "title" in response_data
    assert "image" in response_data

    # 4. Lista os favoritos
    list_resp = await client.get(f"/api/v1/favorites/{client_id}", headers=headers)
    assert list_resp.status_code == 200
    favorites = list_resp.json()
    assert isinstance(favorites, list)
    assert any(fav["product_id"] == 1 for fav in favorites)
