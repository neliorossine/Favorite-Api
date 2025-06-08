from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from fastapi import HTTPException
import logging
import os

# Logger para eventos relacionados ao banco de dados
logger = logging.getLogger(__name__)
log_level = logging.INFO if os.getenv("ENV") != "production" else logging.ERROR
logger.setLevel(log_level)

# Criação do engine assíncrono a partir da URL do banco
try:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)  # echo=True para debug
    logger.info(f"Conexão com o banco de dados estabelecida: {settings.DATABASE_URL}")
except Exception as e:
    logger.error(f"Erro ao conectar ao banco de dados: {e}")
    raise ValueError("Erro ao conectar ao banco de dados. Verifique a variável DATABASE_URL no .env.")

# Criador de sessões assíncronas para uso nas rotas
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base declarativa para os modelos ORM herdarem
Base = declarative_base()

# Função de dependência para injeção de sessão de banco nas rotas
async def get_db():
    """
    Gera uma sessão de banco de dados assíncrona por requisição FastAPI.
    Garante fechamento da conexão ao final da operação.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
