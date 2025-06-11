import asyncio
import json
import os
import aio_pika
from dotenv import load_dotenv
from loguru import logger
from app.core.database import get_db
from app.crud.favorite import add_favorite, get_product_by_id
from app.crud.client import get_client_by_id

# Carrega variáveis de ambiente
load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = os.getenv("QUEUE_NAME")


async def handle_message(body: bytes) -> None:
    """
    Processa uma mensagem da fila RabbitMQ.

    - Valida se o cliente e o produto existem.
    - Adiciona o produto aos favoritos do cliente.
    """
    try:
        data = json.loads(body)
        client_id = data.get("client_id")
        product_id = data.get("product_id")

        logger.info(f"[CONSUMER] Mensagem recebida: {data}")

        async for db in get_db():
            client = await get_client_by_id(db, client_id)
            if not client:
                logger.warning(f"[CONSUMER] Cliente {client_id} não encontrado")
                return

            product = await get_product_by_id(product_id)
            if not product:
                logger.warning(f"[CONSUMER] Produto {product_id} não encontrado")
                return

            await add_favorite(db, client_id, product)
            logger.success(f"[CONSUMER] Favorito salvo: cliente {client_id} → produto {product_id}")
            return

    except Exception as e:
        logger.exception(f"[CONSUMER] Erro ao processar mensagem: {e}")


async def consume() -> None:
    """
    Inicializa o consumidor RabbitMQ e processa mensagens recebidas da fila.
    """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        logger.info(f"[CONSUMER] Aguardando mensagens na fila '{QUEUE_NAME}'...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await handle_message(message.body)

    except Exception as e:
        logger.exception(f"[CONSUMER] Falha ao iniciar consumo: {e}")


if __name__ == "__main__":
    asyncio.run(consume())
