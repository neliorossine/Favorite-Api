# Favorite API v2

API RESTful e GraphQL para gerenciamento de **produtos favoritos por cliente**, com suporte a mensageria via RabbitMQ. Esta versão é uma evolução da branch `main`.

---

## ✨ Funcionalidades Adicionais da `favorite_api_v2`

- ✅ Rota assíncrona de favoritos via RabbitMQ
- ✅ Integração com fila RabbitMQ (`favorites_queue`)
- ✅ Consumer assíncrono para processar os favoritos
- ✅ Suporte a GraphQL via Strawberry
- ✅ Schema GraphQL com consulta de favoritos enriquecidos
- ✅ Testes da fila com fallback (sem depender do Rabbit em testes)

---

## 🚀 Como Executar

```bash
git checkout favorite_api_v2
docker-compose up --build
```

Acesse:

- Swagger UI: http://localhost:8010/docs
- GraphQL Playground: http://localhost:8010/graphql

---

## 📦 Endpoints Adicionais

### 📨 Favoritos via RabbitMQ

- `POST /api/v1/favorites-rabbit/{client_id}` – Envia favorito para a fila RabbitMQ

> Essa rota publica na fila `favorites_queue`. O consumidor recebe e salva no banco de forma assíncrona.

### 🔮 GraphQL

- `POST /graphql` – Consulta de favoritos via GraphQL

```graphql
query {
  favorites(clientId: 1) {
    productId
    title
    price
    review
  }
}
```

---

## ✅ Testes Automatizados

Testes adicionados:

- Teste completo da rota RabbitMQ com fallback
- Integração da fila com o banco de dados
- Testes de GraphQL com consulta de favoritos

---

## 🧩 Estrutura Adicional

```
├── app/
│   ├── api/v1/
│   │   └── favorites_rabbit.py         # Nova rota assíncrona via fila
│   ├── queue/
│   │   ├── producer.py                 # Publica na fila RabbitMQ
│   │   └── consumer.py                 # Worker assíncrono que escuta e salva
│   ├── graphql/
│   │   └── schema.py                   # Schema GraphQL via Strawberry
│   ├── tests/
│   │   └── test_favorites_rabbit.py    # Teste da nova rota assíncrona via fila
```

---

## 🧠 Observações Técnicas

- A fila `favorites_queue` é declarada automaticamente no producer e consumer.
- O teste de integração `test_favorites_rabbit.py` usa `pytest` e `httpx`, com `sleep()` para aguardar o worker.
- GraphQL usa `strawberry.fastapi.GraphQLRouter` com schema separado.

---

## 📌 Observação

Esta branch é ideal para contextos onde:

- Há necessidade de processamento assíncrono com filas
- Integração com múltiplos sistemas (ex: eventos de favoritos)
- Consultas otimizadas via GraphQL para frontends modernos

---
