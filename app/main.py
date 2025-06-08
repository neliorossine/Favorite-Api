from fastapi import FastAPI
from app.api.v1.clients import router as clients_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.products import router as product_router
from app.api.v1.auth import router as auth_router
from app.core.database import engine, Base

def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.
    Inclui rotas, configurações do Swagger, eventos de inicialização e metadados da API.
    """
    app = FastAPI(
        title="Favorite API",
        description=(
            "API RESTful para gerenciamento de clientes e seus produtos favoritos. "
            "Inclui autenticação via JWT e integração com uma API externa de produtos."
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

    # Inclusão das rotas versionadas
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(clients_router, prefix="/api/v1/clients", tags=["clients"])
    app.include_router(favorites_router, prefix="/api/v1/favorites", tags=["favorites"])
    app.include_router(product_router, prefix="/api/v1/products", tags=["products"])

    @app.get("/")
    async def root():
        """
        Rota raiz simples para verificar se a API está online.
        """
        return {"message": "API rodando!"}

    @app.get("/openapi.json")
    async def custom_openapi():
        """
        Geração customizada do esquema OpenAPI com suporte a JWT via BearerAuth.
        """
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
        """
        Evento de inicialização da aplicação. Responsável por criar as tabelas no banco de dados.
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app
