from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.client import get_client_by_id
from app.crud.favorite import get_product_by_id, is_favorite_registered
from app.schemas.schemas import FavoriteCreate
from app.api.v1.auth import get_current_user
from app.queue.producer import publish_favorite_event

router = APIRouter(tags=["favorites-rabbit"])


@router.post("/{client_id}", response_model=dict)
async def create_favorite_rabbit(
    client_id: int,
    favorite: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Envia um produto favorito para ser processado de forma assíncrona via RabbitMQ.

    - O cliente autenticado deve ser o mesmo informado na URL.
    - O produto é validado via API externa.
    - Evita duplicação antes de publicar na fila.
    """
    # Verifica existência do cliente
    client = await get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Garante que o cliente autenticado só modifique seus próprios favoritos
    if client.id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para adicionar favoritos para outro cliente."
        )

    # Valida existência do produto
    product = await get_product_by_id(favorite.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verifica se o favorito já foi adicionado anteriormente
    if await is_favorite_registered(db, client_id, favorite.product_id):
        raise HTTPException(status_code=400, detail="Produto já está nos favoritos")

    # Publica o evento na fila para processamento assíncrono
    await publish_favorite_event({
        "client_id": client_id,
        "product_id": favorite.product_id
    })

    return {
        "message": "Favorito enviado para processamento assíncrono",
        "client_id": client_id,
        "product_id": favorite.product_id
    }
