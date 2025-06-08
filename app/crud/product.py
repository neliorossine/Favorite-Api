import httpx
from fastapi import HTTPException
from app.core.cache import get_cache, set_cache
from typing import List, Optional
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Dados simulados para fallback
fake_product_data = [
    {
        "id": 1,
        "title": "Produto Falso A",
        "image": "https://via.placeholder.com/150",
        "price": 99.99,
        "rating": {"rate": 4.5, "count": 100},
    },
    {
        "id": 2,
        "title": "Produto Falso B",
        "image": "https://via.placeholder.com/150",
        "price": 79.99,
        "rating": {"rate": 4.0, "count": 50},
    },
    {
        "id": 3,
        "title": "Produto Falso C",
        "image": "https://via.placeholder.com/150",
        "price": 49.99,
        "rating": {"rate": 4.2, "count": 75},
    },
]

# ------------------------------------------------------------------------------
# Funções de produto com fallback e cache
# ------------------------------------------------------------------------------

async def get_all_products() -> List[dict]:
    """
    Busca todos os produtos da API externa.
    Em caso de falha, retorna uma lista de produtos simulados.

    Returns:
        List[dict]: Lista de produtos.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://fakestoreapi.com/products")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Erro na requisição para listar produtos: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao buscar produtos: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar produtos: {e}")

    logger.warning("API externa falhou. Usando dados simulados.")
    return fake_product_data


async def get_product_by_id(product_id: int) -> Optional[dict]:
    """
    Busca detalhes de um produto por ID com cache Redis.

    Args:
        product_id (int): ID do produto.

    Returns:
        Optional[dict]: Dados do produto ou None se inválido.
    """
    cache_key = f"product:{product_id}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"https://fakestoreapi.com/products/{product_id}")
            response.raise_for_status()
            product = response.json()

            valid_product = validate_product_data(product)
            if valid_product:
                await set_cache(cache_key, valid_product, expire=300)
                return valid_product
            else:
                logger.warning(f"Produto {product_id} com dados incompletos: {product}")
                return None

    except httpx.RequestError as e:
        logger.error(f"Erro na requisição do produto {product_id}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao buscar produto {product_id}: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar produto {product_id}: {e}")

    logger.warning(f"API externa falhou para produto {product_id}. Usando dados simulados.")
    return fake_product_data[0]


def validate_product_data(product_data: dict) -> Optional[dict]:
    """
    Valida se os dados do produto contêm os campos obrigatórios.

    Args:
        product_data (dict): Dados do produto.

    Returns:
        Optional[dict]: Produto válido ou None.
    """
    required_fields = ["id", "title", "image", "price"]
    if not all(field in product_data for field in required_fields):
        logger.warning(f"Produto inválido: campos ausentes em {product_data}")
        return None
    return product_data
