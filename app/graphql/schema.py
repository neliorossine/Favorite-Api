import strawberry
from typing import List, Optional
from app.core.database import get_db
from app.crud.favorite import get_favorites_by_client, get_product_by_id


@strawberry.type
class Favorite:
    """
    Representa um produto favorito de um cliente com dados enriquecidos da API externa.
    """
    product_id: int
    title: str
    price: float
    review: Optional[float]


@strawberry.type
class Query:
    @strawberry.field(description="Retorna a lista de produtos favoritos de um cliente.")
    async def favorites(self, client_id: int) -> List[Favorite]:
        """
        Consulta os produtos favoritos de um cliente.

        - Utiliza uma sessão assíncrona obtida via `get_db()`.
        - Enriquece os dados dos produtos com informações de uma API externa.
        - Finaliza corretamente o generator da sessão ao fim da execução.

        Args:
            client_id (int): ID do cliente cujos favoritos serão retornados.

        Returns:
            List[Favorite]: Lista de produtos favoritos com título, preço e review.
        """
        db_gen = get_db()
        db = await anext(db_gen)

        try:
            favoritos = await get_favorites_by_client(db, client_id, limit=10, offset=0)

            results: List[Favorite] = []
            for fav in favoritos:
                product_data = await get_product_by_id(fav.product_id)
                if product_data:
                    results.append(Favorite(
                        product_id=fav.product_id,
                        title=product_data["title"],
                        price=product_data["price"],
                        review=product_data.get("rating", {}).get("rate")
                    ))
            return results

        finally:
            await db_gen.aclose()


# Esquema principal do GraphQL
schema = strawberry.Schema(query=Query)
