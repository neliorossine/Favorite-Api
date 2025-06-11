from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Favorite
import httpx
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Dados simulados para fallback
fake_product_data = {
    "id": 1,
    "title": "Produto Falso",
    "image": "https://via.placeholder.com/150",
    "price": 99.99,
    "rating": {"rate": 4.5, "count": 100}
}

# ------------------------------------------------------------------------------
# API externa e fallback
# ------------------------------------------------------------------------------

async def get_product_by_id(product_id: int) -> dict:
    """
    Busca detalhes de um produto pela API externa.
    Em caso de falha, retorna dados simulados (fallback).

    Args:
        product_id (int): ID do produto.

    Returns:
        dict: Dados do produto.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"https://fakestoreapi.com/products/{product_id}")
            response.raise_for_status()
            product = response.json()

            required_fields = ["id", "title", "image", "price"]
            if not all(field in product for field in required_fields):
                logger.warning(f"Produto {product_id} retornou dados incompletos: {product}")
                return None

            return product

    except httpx.RequestError as e:
        logger.error(f"Erro na requisição do produto {product_id}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao buscar produto {product_id}: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar produto {product_id}: {e}")

    logger.warning(f"API externa falhou para o produto {product_id}. Usando dados simulados.")
    return fake_product_data

# ------------------------------------------------------------------------------
# CRUD de favoritos
# ------------------------------------------------------------------------------

async def add_favorite(db: AsyncSession, client_id: int, product_data: dict) -> Favorite:
    """
    Adiciona um produto aos favoritos de um cliente.

    Args:
        db (AsyncSession): Sessão do banco de dados.
        client_id (int): ID do cliente.
        product_data (dict): Dados do produto.

    Returns:
        Favorite: Instância do favorito criado ou existente.
    """
    stmt = select(Favorite).where(
        Favorite.client_id == client_id,
        Favorite.product_id == product_data["id"]
    )
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        logger.info(f"Produto {product_data['id']} já está nos favoritos.")
        return existing

    favorite = Favorite(
        client_id=client_id,
        product_id=product_data["id"],
        title=product_data["title"],
        image=product_data["image"],
        price=product_data["price"],
        review=str(product_data.get("rating", {}).get("rate", ""))
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    logger.info(f"Produto {product_data['id']} adicionado aos favoritos.")
    return favorite

async def get_favorites_by_client(db: AsyncSession, client_id: int, limit: int = 10, offset: int = 0):
    """
    Retorna a lista de favoritos de um cliente com paginação.

    Args:
        db (AsyncSession): Sessão do banco de dados.
        client_id (int): ID do cliente.
        limit (int): Número máximo de resultados.
        offset (int): Quantidade de itens a pular.

    Returns:
        list[Favorite]: Lista de produtos favoritos.
    """
    result = await db.execute(
        select(Favorite)
        .where(Favorite.client_id == client_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()

async def remove_favorite(db: AsyncSession, client_id: int, product_id: int) -> bool:
    """
    Remove um produto da lista de favoritos de um cliente.

    Args:
        db (AsyncSession): Sessão do banco de dados.
        client_id (int): ID do cliente.
        product_id (int): ID do produto.

    Returns:
        bool: True se removido, False se não encontrado.
    """
    stmt = select(Favorite).where(
        Favorite.client_id == client_id,
        Favorite.product_id == product_id
    )
    result = await db.execute(stmt)
    favorite = result.scalars().first()

    if not favorite:
        logger.warning(f"Produto {product_id} não encontrado nos favoritos do cliente {client_id}.")
        return False

    await db.delete(favorite)
    await db.commit()
    logger.info(f"Produto {product_id} removido dos favoritos do cliente {client_id}.")
    return True

async def is_favorite_registered(db: AsyncSession, client_id: int, product_id: int) -> bool:
    """
    Verifica se o produto já foi favoritado por esse cliente.
    """
    result = await db.execute(
        select(Favorite).where(
            Favorite.client_id == client_id,
            Favorite.product_id == product_id
        )
    )
    return result.scalars().first() is not None
