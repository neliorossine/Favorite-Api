import os
from dotenv import load_dotenv

# Força o uso do SQLite em memória para testes
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Carrega variáveis de ambiente de um arquivo alternativo (.env.dev)
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env.dev")
load_dotenv(dotenv_path=dotenv_path, override=True)

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import create_app
from app.core.database import Base

# Configuração do banco assíncrono para testes
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def prepare_db():
    """
    Fixture para preparar o banco de dados antes de cada teste.
    Garante que as tabelas estejam criadas e limpas.
    """
    import app.models.models  # Garante que Client e Favorite sejam registrados no Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    """
    Fixture que fornece uma sessão de banco assíncrona para testes.
    """
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(prepare_db):
    """
    Fixture que retorna um cliente HTTP para testes, com banco preparado.
    """
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
