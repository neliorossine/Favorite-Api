import redis.asyncio as redis
import json
import logging
from typing import Optional

# Configuração do logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# URL padrão do Redis (pode ser movida para .env futuramente)
REDIS_URL = "redis://redis:6379"
redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def get_cache(key: str) -> Optional[dict]:
    """
    Recupera um valor do Redis a partir de uma chave.

    Args:
        key (str): A chave do cache.

    Returns:
        dict | None: O valor armazenado (deserializado), ou None se não encontrado ou erro.
    """
    try:
        data = await redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.warning(f"[Redis] Erro ao ler cache para '{key}': {e}")
        return None


async def set_cache(key: str, value: dict, expire: int = 300):
    """
    Armazena um valor no Redis com expiração (TTL).

    Args:
        key (str): A chave para armazenar o valor.
        value (dict): O valor a ser armazenado.
        expire (int): Tempo de expiração em segundos (padrão: 5 minutos).
    """
    try:
        await redis_client.set(key, json.dumps(value), ex=expire)
    except Exception as e:
        logger.warning(f"[Redis] Erro ao salvar cache para '{key}': {e}")
