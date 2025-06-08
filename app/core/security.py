from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from app.core.config import settings

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticação HTTP Bearer (JWT)
security = HTTPBearer()

# Variáveis de configuração vindas do .env
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
TOKEN_EXPIRE_MINUTES = settings.TOKEN_EXPIRE_MINUTES

def hash_password(password: str) -> str:
    """
    Gera o hash de uma senha em texto puro usando bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_token(email: str, expires_delta: Optional[int] = None) -> str:
    """
    Cria um token JWT com base no e-mail fornecido.

    Args:
        email (str): E-mail do usuário para incluir no token.
        expires_delta (Optional[int]): Tempo de expiração em minutos. Se omitido, usa valor padrão do settings.

    Returns:
        str: Token JWT codificado.
    """
    to_encode = {"sub": email}
    expires_delta = timedelta(minutes=expires_delta or TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    """
    Verifica a validade de um token JWT e extrai o e-mail do payload.

    Args:
        token (str): Token JWT a ser verificado.

    Returns:
        str: E-mail do usuário se o token for válido.

    Raises:
        HTTPException: Se o token for inválido ou expirado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
