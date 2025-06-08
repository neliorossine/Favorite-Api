# Favorite API
<br>
API RESTful para gerenciamento de **produtos favoritos por cliente**, desenvolvida para o desafio técnico Magazine Luiza / Aiqfome.
<br>
<br>

---
<br>

### ✨ Funcionalidades

<br>

- ✅ Cadastro e autenticação de usuários (JWT)
- ✅ CRUD de clientes (nome e e-mail únicos)
- ✅ Adição e listagem de produtos favoritos por cliente
- ✅ Integração com API externa [`FakeStoreAPI`](https://fakestoreapi.com)
- ✅ Cache com Redis para melhorar performance
- ✅ Proteção com autenticação (JWT Bearer Token)
- ✅ Testes automatizados com `pytest` e `httpx`
- ✅ Documentação automática via Swagger/OpenAPI

<br>

---

<br>

### 🛠️ Tecnologias Utilizadas

<br>

- **Python 3.11**
- **FastAPI**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Redis (cache)**
- **SQLAlchemy**
- **JWT**
- **Pytest**

<br>

---
<br>

### 🚀 Como Executar o Projeto

<br>

### ✅ Requisitos

- Docker + Docker Compose

<br>

### ▶️ Subir a aplicação com Docker

```bash
git clone https://github.com/neliorossine/favorite_api.git
cd favorite_api

# Crie o arquivo de variáveis
cp .env.example .env

# Suba todos os serviços
docker-compose up --build
```

<br>

---


<br>


### 🔐 Autenticação

<br>

- Registre um novo usuário via: `POST /api/v1/auth/signup`
- Faça login via: `POST /api/v1/auth/login`
- Use o token JWT no header das rotas protegidas:

```
Authorization: Bearer <seu_token>
```


<br>

---


<br>

### 📦 Endpoints Principais

<br>

### 📁 Clientes

- `POST /clients/` – Criação de cliente
- `GET /clients/` – Listagem
- `PUT /clients/{id}` – Atualização
- `DELETE /clients/{id}` – Remoção

<br>

### ❤️ Favoritos

- `POST /favorites/` – Adiciona produto à lista de favoritos
- `GET /favorites/{client_id}` – Lista favoritos de um cliente

> Produtos duplicados não são permitidos. A API valida a existência do produto via [FakeStoreAPI](https://fakestoreapi.com).

<br>

### 🛒 Produtos

- `GET /products/` – Lista todos os produtos
- `GET /products/{id}` – Detalhes de um produto específico

<br>

---

<br>

### 🛍️ Exemplo de Requisição: Adicionar Produto Favorito

<br>

```
curl -X POST http://localhost:8010/api/v1/favorites \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1, "product_id": 5}'
```

<br>

---

<br>


### ✅ Rodando os Testes

<br>

```bash
pytest -v
```

<br>


Testes incluídos:

- Autenticação (`test_auth.py`)
- CRUD de clientes (`test_clients.py`)
- Favoritos (criação, duplicidade, listagem) (`test_favorites.py`)
- Produtos (visualização, listagem) (`test_products.py`)

<br>

---

<br>

### 📦 Estrutura do Projeto

<br>


```
favorite_api/
├── app/
│   ├── main.py                          # Entrada principal da API
│   ├── api/v1/                          # Rotas organizadas por versão
│   │   ├── auth.py
│   │   ├── clients.py
│   │   ├── favorites.py
│   │   └── products.py
│   ├── core/                            # Config, segurança, cache e DB
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── cache.py                     # Redis
│   ├── crud/                            # Regras de negócio
│   │   ├── client.py
│   │   ├── favorite.py
│   │   └── product.py
│   ├── models/                          # ORM SQLAlchemy
│   │   └── models.py
│   └── schemas/                         # Schemas Pydantic
│       └── schemas.py
├── tests/                               # Testes organizados por domínio
│   ├── test_auth.py
│   ├── test_clients.py
│   ├── test_favorites.py
│   ├── test_products.py
│   └── conftest.py                      # Fixtures
├── Dockerfile                           # Imagem com wait-for-it + Uvicorn
├── docker-compose.yml                   # API + DB PostgreSQL + Redis
├── requirements.txt                     # Dependências
├── .env / .env.example                  # Variáveis ambiente
├── README.md                            
```

<br>

---

<br>


### 📌 Decisões Técnicas

<br>

- Redis: utilizado como cache para melhorar a performance e reduzir chamadas repetidas à API externa de produtos.
- JWT: autenticação segura baseada em tokens com tempo de expiração e validação em todas as rotas protegidas.
- Arquitetura modular e escalável: separação clara por domínios (clients, favorites, products) seguindo boas práticas de organização.
- Segurança: rotas protegidas utilizando Depends(get_current_user) e validação robusta do token JWT.
- API Externa resiliente: integração com a FakeStoreAPI para validação de produtos, com fallback opcional para garantir disponibilidade em caso de falha da API externa.

<br>

---

<br>

### 🤝 Autor

Desenvolvido por Nélio Rossine de Oliveira — desafio técnico Magazine Luiza (2025).

