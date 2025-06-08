from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import ClientLogin, ClientCreate
from app.crud.client import authenticate_client, get_client_by_email
from app.core.security import create_token, verify_token, hash_password
from app.models.models import Client

router = APIRouter(tags=["auth"])

# Esquema de autenticação HTTP Bearer
security = HTTPBearer()


@router.post("/signup")
async def signup(
    form_data: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cria um novo cliente.

    - **name**: Nome do cliente
    - **email**: E-mail único
    - **password**: Senha (será criptografada)
    - **confirm_password**: Confirmação da senha
    """
    existing_client = await get_client_by_email(db, form_data.email)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    hashed_password = hash_password(form_data.password)
    new_client = Client(
        name=form_data.name,
        email=form_data.email,
        hashed_password=hashed_password,
    )

    db.add(new_client)
    await db.commit()
    return {
        "msg": "Usuário criado com sucesso",
        "id": new_client.id,
        "email": new_client.email
    }


@router.post("/login")
async def login(
    form_data: ClientLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Autentica o cliente e retorna um token JWT.

    - **email**: E-mail do cliente
    - **password**: Senha do cliente
    """
    client = await authenticate_client(db, form_data.email, form_data.password)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    token = create_token(client.email)
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(
    authorization: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna o cliente autenticado a partir do token JWT.
    """
    try:
        token = authorization.credentials
        email = verify_token(token)
        client = await get_client_by_email(db, email)

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )

        return client

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
