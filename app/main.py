from fastapi import FastAPI
from app.api.v1.clients import router as clients_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.products import router as product_router
from app.api.v1.auth import router as auth_router
from app.api.v1.favorites_rabbit import router as favorites_rabbit_router
from app.core.database import engine, Base
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema


def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.
    Inclui rotas, configurações do Swagger, eventos de inicialização e metadados da API.
    """
    app = FastAPI(
        title="Favorite API",
        description=(
            "API RESTful para gerenciamento de clientes e seus produtos favoritos.\n\n"
            "- Inclui autenticação via JWT.\n"
            "- Integração com API externa de produtos.\n"
            "- Suporte a mensageria com RabbitMQ.\n"
            "- Suporte a GraphQL via Strawberry.\n\n"
            "🔗 Acesse o [GraphQL Playground (GraphiQL)](/graphql) para testar queries."
        ),
        version="1.0.0",
        contact={
            "name": "Nélio Rossine de Oliveira",
            "url": "https://github.com/neliorossine",
            "email": "junior.rossine@outlook.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        }
    )

    # Rotas REST
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(clients_router, prefix="/api/v1/clients", tags=["clients"])
    app.include_router(favorites_router, prefix="/api/v1/favorites", tags=["favorites"])
    app.include_router(product_router, prefix="/api/v1/products", tags=["products"])
    app.include_router(favorites_rabbit_router, prefix="/api/v1/favorites-rabbit", tags=["favorites-rabbit"])

    # Rota GraphQL
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])

    @app.get("/")
    async def root():
        return {"message": "API rodando!"}

    @app.get("/openapi.json")
    async def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = app.get_openapi()
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    @app.on_event("startup")
    async def on_startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app
