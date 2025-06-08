from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.crud.favorite import (
    add_favorite,
    get_favorites_by_client,
    remove_favorite,
    get_product_by_id,
)
from app.schemas.schemas import FavoriteCreate, FavoriteOut
from app.api.v1.auth import get_current_user
from app.crud.client import get_client_by_id

router = APIRouter(tags=["favorites"])


@router.get("/{client_id}", response_model=List[FavoriteOut])
async def list_favorites(
    client_id: int,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna a lista de produtos favoritos de um cliente específico.

    - Requer autenticação.
    - O cliente autenticado só pode acessar seus próprios favoritos.
    - Os dados retornados incluem informações completas dos produtos (título, imagem, preço e review).
    """
    client = await get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if client.id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para acessar os favoritos desse cliente.")

    favorites = await get_favorites_by_client(db, client_id, limit=limit, offset=offset)

    full_favorites = []
    for favorite in favorites:
        product_data = await get_product_by_id(favorite.product_id)
        if product_data:
            favorite_data = {
                "id": favorite.id,
                "client_id": favorite.client_id,
                "product_id": favorite.product_id,
                "title": product_data["title"],
                "image": product_data["image"],
                "price": product_data["price"],
                "review": product_data.get("rating", {}).get("rate", None)
            }
            full_favorites.append(favorite_data)

    return full_favorites


@router.post("/{client_id}", response_model=FavoriteOut)
async def create_favorite(
    client_id: int,
    favorite: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Adiciona um novo produto aos favoritos do cliente autenticado.

    - O cliente autenticado deve ser o mesmo informado na URL.
    - O produto é validado via API externa antes de ser salvo.
    - Se o produto já estiver nos favoritos, uma exceção será lançada.
    """
    client = await get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if client.id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para adicionar favoritos para outro cliente.")

    product = await get_product_by_id(favorite.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    existing_favorites = await get_favorites_by_client(db, client_id)
    if any(fav.product_id == favorite.product_id for fav in existing_favorites):
        raise HTTPException(status_code=400, detail="Produto já está nos favoritos")

    return await add_favorite(db, client_id, product)


@router.delete("/{client_id}/{product_id}", response_model=dict)
async def delete_favorite(
    client_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove um produto da lista de favoritos do cliente autenticado.

    - O cliente autenticado deve ser o mesmo informado na URL.
    - Caso o produto não esteja nos favoritos, retorna erro 404.
    """
    client = await get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if client.id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para remover favoritos de outro cliente.")

    removed = await remove_favorite(db, client_id, product_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")

    return {"message": f"Produto favorito {product_id} removido do cliente {client_id}"}
