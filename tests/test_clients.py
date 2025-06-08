import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import create_app
from app.core.database import engine
from app.models.models import Base

app = create_app()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_clients_crud_flow(client):
    """
    Teste completo de fluxo de CRUD de clientes, incluindo:
    - Signup + Login
    - Criação de outro cliente
    - Listagem
    - Busca por ID
    - Tentativa de atualizar/deletar outro cliente (esperado: 403)
    """

    # 1. Cadastro
    signup_resp = await client.post("/api/v1/auth/signup", json={
        "name": "Test User",
        "email": "testclient@example.com",
        "password": "testpassword",
        "confirm_password": "testpassword"
    })
    assert signup_resp.status_code == 200

    # 2. Login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "testclient@example.com",
        "password": "testpassword"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Criar cliente (outro usuário)
    create_resp = await client.post("/api/v1/clients/", json={
        "name": "João da Silva",
        "email": "joao@example.com",
        "password": "12345678",
        "confirm_password": "12345678"
    }, headers=headers)
    assert create_resp.status_code == 200
    client_data = create_resp.json()
    assert client_data["email"] == "joao@example.com"
    client_id = client_data["id"]

    # 4. Listar clientes
    list_resp = await client.get("/api/v1/clients/", headers=headers)
    assert list_resp.status_code == 200
    assert any(c["id"] == client_id for c in list_resp.json())

    # 5. Buscar cliente por ID
    retrieve_resp = await client.get(f"/api/v1/clients/{client_id}", headers=headers)
    assert retrieve_resp.status_code == 200
    assert retrieve_resp.json()["email"] == "joao@example.com"

    # 6. Atualizar cliente (não autorizado)
    update_resp = await client.put(f"/api/v1/clients/{client_id}", json={
        "name": "João Atualizado",
        "email": "joao@example.com"
    }, headers=headers)
    assert update_resp.status_code == 403
    # assert "não autorizado" in update_resp.json()["detail"].lower()

    # 7. Deletar cliente (não autorizado)
    delete_resp = await client.delete(f"/api/v1/clients/{client_id}", headers=headers)
    assert delete_resp.status_code == 403
    # assert "não autorizado" in delete_resp.json()["detail"].lower()
