import asyncio
import os
from typing import Callable, Any

from tc_messageBroker import RabbitMQ

from logger.embedding_logger import logger
from utils import constants


class EventBroker:
    def __init__(self):

        self.broker_url = constants.RABBITMQ_HOST
        self.port = constants.RABBITMQ_PORT
        self.username = constants.RABBITMQ_USER
        self.password = constants.RABBITMQ_PASS

        logger.info(f"__init__ broker_url: {self.broker_url}:{self.port}")

    async def a_listen(self, queue: str, event: str, callback: Callable):
        asyncio.get_event_loop().run_in_executor(None, self.listen, queue, event, callback)

    def listen(self, queue: str, event: str, callback: Callable):
        logger.debug("listening %s", queue)

        logger.info(f"broker_url: {self.broker_url}:{self.port}")

        rabbit_mq = RabbitMQ(
            broker_url=self.broker_url, port=self.port, username=self.username, password=self.password
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

    async def a_publish(self, queue: str, event: str, content: dict[str, Any] | None):
        asyncio.get_event_loop().run_in_executor(None, self.publish, queue, event, content)

    def publish(self, queue: str, event: str, content: dict[str, Any] | None):
        logger.debug("publishing %s", content)

        rabbit_mq = RabbitMQ(
            broker_url=self.broker_url, port=self.port, username=self.username, password=self.password
        )

        rabbit_mq.connect(queue)

        if content is None:
            content = {"uuid": "d99a1490-fba6-11ed-b9a9-0d29e7612dp8", "data": "some results"}

        rabbit_mq.publish(
            queue,
            event=event,
            content=content,
        )
