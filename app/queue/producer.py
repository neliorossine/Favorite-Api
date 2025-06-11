import json
import os

import aio_pika
from aio_pika import Message
from dotenv import load_dotenv
from loguru import logger

# Carrega variáveis de ambiente do .env
load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")


async def publish_favorite_event(payload: dict) -> None:
    """
    Publica uma mensagem JSON na fila do RabbitMQ com os dados de um produto favorito.

    Esta função utiliza uma conexão robusta com o RabbitMQ, garante que a fila esteja
    declarada (idempotente) e publica uma mensagem no formato JSON com os dados do cliente
    e do produto.

    Args:
        payload (dict): Um dicionário com os campos obrigatórios:
            - client_id (int): ID do cliente
            - product_id (int): ID do produto favorito

        Exemplo:
            {
                "client_id": 1,
                "product_id": 3
            }

    Logs:
        - Log de debug no início da publicação.
        - Log de sucesso ao publicar.
        - Log de erro detalhado em caso de falha.
    """
    try:
        logger.debug(f"[RABBITMQ] Iniciando publicação: {payload}")

        # Aguarda a conexão e entra no contexto assíncrono
        async with (await aio_pika.connect_robust(RABBITMQ_URL)) as connection:
            channel = await connection.channel()

            # Declara a fila (idempotente)
            await channel.declare_queue(QUEUE_NAME, durable=True)

            # Cria a mensagem
            message = Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json"
            )

            # Publica a mensagem
            await channel.default_exchange.publish(
                message,
                routing_key=QUEUE_NAME
            )

            logger.success(f"[RABBITMQ] Mensagem publicada com sucesso: {payload}")

    except Exception as e:
        logger.exception(f"[RABBITMQ] Falha ao publicar mensagem: {e}")
