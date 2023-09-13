import asyncio
from typing import Callable, Any

from tc_messageBroker import RabbitMQ

from logger.hivemind_logger import logger


def do_something(received_data):
    A = 2 * 2
    message = f"Calculation Results: {A}"
    print(message)
    print(f"received_data: {received_data}")

async def a_listen(queue: str, event: str, callback: Callable):
    asyncio.get_event_loop().run_in_executor(None, listen, queue, event, callback)

def listen(queue: str, event: str, callback: Callable):
    logger.debug("listening %s", queue)
    broker_url = "localhost"
    port = 5672
    username = "guest"
    password = "guest"

    rabbit_mq = RabbitMQ(
        broker_url=broker_url, port=port, username=username, password=password
    )

    rabbit_mq.on_event(event, callback)

    print("Waiting for messages...")
    rabbit_mq.connect(queue)
    print("Connected to broker successfully!")

    rabbit_mq.consume(queue)
    print("consume messages...")
    if rabbit_mq.channel is not None:
        print("listening messages...")
        try:
            rabbit_mq.channel.start_consuming()
            print("Never reach here!")
        except KeyboardInterrupt:
            rabbit_mq.channel.stop_consuming()
            print("Disconnected from broker successfully!")
    else:
        print("Connection to broker was not successful!")


async def a_publish(queue: str, event: str, content: dict[str, Any] | None):
    asyncio.get_event_loop().run_in_executor(None, publish, queue, event, content)

def publish(queue: str, event: str, content: dict[str, Any] | None):
    logger.debug("publishing %s", content)
    broker_url = "localhost"
    port = 5672
    username = "guest"
    password = "guest"

    rabbit_mq = RabbitMQ(
        broker_url=broker_url, port=port, username=username, password=password
    )

    rabbit_mq.connect(queue)

    if content is None:
        content = {"uuid": "d99a1490-fba6-11ed-b9a9-0d29e7612dp8", "data": "some results"}

    rabbit_mq.publish(
        queue,
        event=event,
        content=content,
    )
