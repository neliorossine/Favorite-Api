import os
from dotenv import load_dotenv

# Carrega .env.dev primeiro
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env.dev")
load_dotenv(dotenv_path=dotenv_path, override=True)

# Força o uso de SQLite em memória para testes
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
DATABASE_URL = os.environ["DATABASE_URL"]

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Agora sim importa os módulos internos com DATABASE_URL correto
from app.main import create_app
from app.core.database import Base

# Configuração do engine e session para testes
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def prepare_db():
    """
    Prepara o banco SQLite para cada teste com tabelas limpas.
    """
    import app.models.models  # Garante que os modelos sejam registrados

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    """
    Retorna uma sessão assíncrona do banco de testes.
    """
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(prepare_db):
    """
    Cliente HTTP com banco limpo para cada teste.
    """
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
