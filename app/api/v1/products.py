from fastapi import APIRouter, HTTPException
import httpx
import logging
from typing import List
from pydantic import BaseModel, HttpUrl

from app.core.cache import get_cache, set_cache

# Configuração de logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dados de fallback em caso de falha na API externa
fake_products = [
    {"id": 1, "title": "Produto A", "image": "https://via.placeholder.com/150", "price": 99.99,
     "rating": {"rate": 4.5, "count": 100}},
    {"id": 2, "title": "Produto B", "image": "https://via.placeholder.com/150", "price": 79.99,
     "rating": {"rate": 4.0, "count": 50}},
    {"id": 3, "title": "Produto C", "image": "https://via.placeholder.com/150", "price": 49.99,
     "rating": {"rate": 4.2, "count": 75}},
]

# Modelo de produto
class Product(BaseModel):
    id: int
    title: str
    image: HttpUrl
    price: float
    rating: dict

router = APIRouter(tags=["products"])


async def fetch_products() -> List[Product]:
    """
    Busca todos os produtos da API externa. Em caso de erro ou timeout, retorna dados simulados.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://fakestoreapi.com/products")
            response.raise_for_status()
            return [Product(**product) for product in response.json()]
    except (httpx.TimeoutException, httpx.RequestError):
        logger.warning("API externa demorou ou falhou. Retornando dados simulados.")
        return [Product(**product) for product in fake_products]


@router.get("/", response_model=List[Product])
async def list_products():
    """
    Lista todos os produtos disponíveis.

    Retorna os dados da API externa, ou fallback simulado se a API estiver indisponível.
    """
    return await fetch_products()


async def fetch_product_details(product_id: int) -> Product:
    """
    Busca os detalhes de um produto específico, com cache Redis.

    - Primeiro tenta obter do cache.
    - Se não existir no cache, busca na API externa.
    - Em caso de falha, retorna um produto simulado.
    """
    cache_key = f"product:{product_id}"
    cached = await get_cache(cache_key)
    if cached:
        logger.info(f"[CACHE] Produto {product_id} retornado do Redis")
        return Product(**cached)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"https://fakestoreapi.com/products/{product_id}")
            response.raise_for_status()
            product_data = response.json()

            await set_cache(cache_key, product_data, expire=300)
            logger.info(f"[API] Produto {product_id} buscado da API externa")
            return Product(**product_data)

    except (httpx.TimeoutException, httpx.RequestError):
        logger.warning(f"Falha ao buscar produto {product_id}. Usando dados simulados.")
        return Product(**fake_products[0])

    raise HTTPException(status_code=404, detail="Produto não encontrado")


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """
    Retorna os detalhes de um produto pelo ID, com uso de cache Redis.
    """
    return await fetch_product_details(product_id)
