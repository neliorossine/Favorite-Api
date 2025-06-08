import pytest
from fastapi.testclient import TestClient
from unittest import mock
import httpx
from app.main import create_app  # Certifique-se de importar a função corretamente

# Criando uma instância do cliente de teste
@pytest.fixture
def client():
    app = create_app()  # Cria a instância do app
    return TestClient(app)  # Retorna o TestClient com a instância do app

@pytest.fixture
def mock_httpx_get():
    with mock.patch("httpx.AsyncClient.get", new_callable=mock.AsyncMock) as mock_get:
        # Garantindo que o retorno da resposta seja assíncrono
        mock_get.return_value.__aenter__.return_value.status_code = 200
        mock_get.return_value.__aenter__.return_value.json = mock.AsyncMock(return_value=[
            {"id": 1, "title": "Produto A", "image": "https://via.placeholder.com/150", "price": 99.99,
             "rating": {"count": 100, "rate": 4.5}},
            {"id": 2, "title": "Produto B", "image": "https://via.placeholder.com/150", "price": 49.99,
             "rating": {"count": 75, "rate": 4.2}},
            {"id": 3, "title": "Produto C", "image": "https://via.placeholder.com/150", "price": 29.99,
             "rating": {"count": 50, "rate": 3.8}},
        ])
        yield mock_get


def test_list_products(client, mock_httpx_get):
    # Simulando a resposta da API externa com dados corretos
    mock_httpx_get.return_value.status_code = 200
    mock_httpx_get.return_value.json = mock.Mock(return_value=[
        {"id": 1, "title": "Produto A", "image": "https://via.placeholder.com/150", "price": 99.99,
         "rating": {"count": 100, "rate": 4.5}},
        {"id": 2, "title": "Produto B", "image": "https://via.placeholder.com/150", "price": 49.99,
         "rating": {"count": 75, "rate": 4.2}},
        {"id": 3, "title": "Produto C", "image": "https://via.placeholder.com/150", "price": 29.99,
         "rating": {"count": 50, "rate": 3.8}},
    ])

    response = client.get("/api/v1/products/")

    assert response.status_code == 200
    assert len(response.json()) == 3  # Espera 3 produtos simulados
    assert response.json()[0]["title"] == "Produto A"  # Verificando o título do primeiro produto
    assert response.json()[1]["title"] == "Produto B"
    assert response.json()[2]["title"] == "Produto C"


def test_get_product(client, mock_httpx_get):
    # Simulando a resposta da API externa para um único produto
    mock_httpx_get.return_value.status_code = 200
    mock_httpx_get.return_value.json = mock.Mock(
        return_value={"id": 1, "title": "Produto A", "image": "https://via.placeholder.com/150", "price": 99.99,
                      "rating": {"count": 100, "rate": 4.5}})

    response = client.get("/api/v1/products/1")

    assert response.status_code == 200
    assert response.json()["title"] == "Produto A"  # Verificando se o título do produto está correto


def test_get_product_timeout(client, mock_httpx_get):
    # Simulando um erro de timeout na resposta da API externa
    mock_httpx_get.side_effect = httpx.TimeoutException("API externa demorou demais para responder")

    # Simulando que a resposta será um fallback devido ao timeout
    response = client.get("/api/v1/products/999")  # Simulando um produto não encontrado, mas com fallback

    assert response.status_code == 200
