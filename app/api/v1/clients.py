from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.crud.client import (
    create_client,
    get_client_by_id,
    get_all_clients,
    update_client,
    delete_client
)
from app.schemas.schemas import ClientCreate, ClientOut, ClientUpdate
from app.api.v1.auth import get_current_user

router = APIRouter(tags=["clients"])


@router.post("/", response_model=ClientOut)
async def create(
    client: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cria um novo cliente.

    - Requer autenticação.
    - Os dados são validados via schema `ClientCreate`.
    """
    return await create_client(db, client)


@router.get("/", response_model=List[ClientOut])
async def list_clients(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna a lista de todos os clientes cadastrados.

    - Requer autenticação.
    """
    return await get_all_clients(db)


@router.get("/{client_id}", response_model=ClientOut)
async def retrieve_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna os dados de um cliente específico pelo ID.

    - Requer autenticação.
    """
    client = await get_client_by_id(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.put("/{client_id}", response_model=ClientOut)
async def update(
    client_id: int,
    client: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Atualiza os dados do cliente autenticado.

    - Só permite atualização dos próprios dados.
    """
    if client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: não é possível atualizar outro cliente."
        )

    updated_client = await update_client(db, client_id, client)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return updated_client


@router.delete("/{client_id}", response_model=dict)
async def delete(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Exclui a conta do cliente autenticado.

    - Só permite exclusão dos próprios dados.
    """
    if client_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: não é possível excluir outro cliente."
        )

    success = await delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"message": f"Cliente {client_id} excluído com sucesso"}
