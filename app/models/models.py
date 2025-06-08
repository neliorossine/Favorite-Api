from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    DateTime,
    Float,
    func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    """
    Modelo que representa um cliente da aplicação.

    Atributos:
        id (int): Identificador único do cliente.
        name (str): Nome completo do cliente.
        email (str): E-mail do cliente (deve ser único).
        hashed_password (str): Senha criptografada.
        created_at (datetime): Data de criação do registro.
        updated_at (datetime): Data da última atualização.
        favorites (List[Favorite]): Relação com produtos favoritos.
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    favorites = relationship(
        "Favorite",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Favorite(Base):
    """
    Modelo que representa um produto marcado como favorito por um cliente.

    Atributos:
        id (int): Identificador único do favorito.
        client_id (int): Referência ao cliente que favoritou.
        product_id (int): ID do produto favorito.
        title (str): Título do produto.
        image (str): URL da imagem do produto.
        price (float): Preço do produto.
        review (str): Avaliação do produto (ex: nota).
        created_at (datetime): Data em que o produto foi favoritado.
        deleted_at (datetime): Campo opcional para soft delete.
    """
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    review = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("client_id", "product_id", name="unique_favorite_per_client"),
    )
