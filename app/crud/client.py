from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.models import Client
from app.schemas.schemas import ClientCreate, ClientUpdate
from app.core.security import hash_password, verify_password

# ---------------------------------------------------------------------
# CRUD de Cliente
# ---------------------------------------------------------------------

async def create_client(db: AsyncSession, client: ClientCreate):
    """
    Cria um novo cliente no banco de dados.

    Args:
        db (AsyncSession): Sessão de banco de dados.
        client (ClientCreate): Dados para criação do cliente.

    Returns:
        Client: Instância do cliente criado.

    Raises:
        HTTPException: Se o e-mail já estiver cadastrado.
    """
    stmt = select(Client).where(Client.email == client.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    hashed_pwd = hash_password(client.password)
    new_client = Client(name=client.name, email=client.email, hashed_password=hashed_pwd)

    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    return new_client

async def get_client_by_id(db: AsyncSession, client_id: int) -> Client:
    """
    Busca um cliente pelo ID.

    Args:
        db (AsyncSession): Sessão de banco de dados.
        client_id (int): ID do cliente.

    Returns:
        Client: Cliente encontrado.

    Raises:
        HTTPException: Se o cliente não for encontrado.
    """
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return client

async def get_client_by_email(db: AsyncSession, email: str) -> Client:
    """
    Busca um cliente pelo e-mail.

    Args:
        db (AsyncSession): Sessão de banco de dados.
        email (str): E-mail do cliente.

    Returns:
        Client | None: Cliente encontrado ou None.
    """
    result = await db.execute(select(Client).where(Client.email == email))
    return result.scalars().first()

async def get_all_clients(db: AsyncSession):
    """
    Lista todos os clientes.

    Args:
        db (AsyncSession): Sessão de banco de dados.

    Returns:
        list[Client]: Lista de clientes.
    """
    result = await db.execute(select(Client))
    return result.scalars().all()

async def update_client(db: AsyncSession, client_id: int, client: ClientUpdate):
    """
    Atualiza os dados de um cliente existente.

    Args:
        db (AsyncSession): Sessão de banco de dados.
        client_id (int): ID do cliente a ser atualizado.
        client (ClientUpdate): Novos dados.

    Returns:
        Client: Cliente atualizado.

    Raises:
        HTTPException: Se o e-mail estiver em uso ou ocorrer erro de integridade.
    """
    existing = await get_client_by_id(db, client_id)

    if client.email:
        result = await db.execute(
            select(Client).where(Client.email == client.email, Client.id != client_id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mail já está em uso por outro cliente."
            )

    for key, value in client.dict(exclude_unset=True).items():
        setattr(existing, key, value)

    try:
        await db.commit()
        await db.refresh(existing)
        return existing
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro de integridade ao atualizar cliente. Verifique se os dados são válidos."
        )

async def delete_client(db: AsyncSession, client_id: int):
    """
    Exclui um cliente do banco de dados.

    Args:
        db (AsyncSession): Sessão de banco de dados.
        client_id (int): ID do cliente a ser excluído.

    Returns:
        dict: Mensagem de sucesso.

    Raises:
        HTTPException: Se o cliente não for encontrado.
    """
    existing = await get_client_by_id(db, client_id)
    await db.delete(existing)
    await db.commit()
    return {"message": f"Cliente {client_id} excluído com sucesso"}

# ---------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------

async def authenticate_client(db: AsyncSession, email: str, password: str):
    """
    Autentica um cliente com e-mail e senha.

    Args:
        db (AsyncSession): Sessão de banco de dados.
        email (str): E-mail do cliente.
        password (str): Senha em texto plano.

    Returns:
        Client: Cliente autenticado.

    Raises:
        HTTPException: Se as credenciais forem inválidas.
    """
    client = await get_client_by_email(db, email)

    if not client or not verify_password(password, client.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    return client
