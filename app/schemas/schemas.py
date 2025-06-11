from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional


# ============================
# CLIENTES
# ============================

class ClientBase(BaseModel):
    """
    Esquema base para um cliente (usado em leitura e escrita).
    """
    name: str = Field(..., example="João Silva")
    email: EmailStr = Field(..., example="joao.silva@example.com")


class ClientCreate(ClientBase):
    """
    Esquema para criação de um novo cliente.
    """
    password: constr(min_length=8) = Field(..., example="senhaSegura123")


class ClientUpdate(BaseModel):
    """
    Esquema para atualização de dados do cliente.
    """
    name: Optional[str] = Field(None, example="João Silva")
    email: Optional[EmailStr] = Field(None, example="joao.silva@example.com")


class ClientLogin(BaseModel):
    """
    Esquema para login do cliente.
    """
    email: EmailStr = Field(..., example="joao.silva@example.com")
    password: str = Field(..., example="senhaSegura123")


class ClientOut(ClientBase):
    """
    Esquema de resposta com dados do cliente.
    """
    id: int = Field(..., example=1)

    class Config:
        orm_mode = True


# ============================
# FAVORITOS
# ============================

class FavoriteBase(BaseModel):
    """
    Esquema base de um favorito (produto favorito de um cliente).
    """
    product_id: int = Field(..., example=1)


class FavoriteCreate(FavoriteBase):
    """
    Esquema para criação de um favorito.
    """
    pass


class FavoriteOut(FavoriteBase):
    """
    Esquema de saída de um favorito com dados do produto.
    """
    id: int = Field(..., example=10)
    title: str = Field(..., example="Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops")
    image: str = Field(..., example="https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg")
    price: float = Field(..., example=109.95)
    review: Optional[str] = Field(None, example="4.5")

    class Config:
        orm_mode = True
