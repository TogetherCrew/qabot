import asyncio
import os
import threading
from typing import Callable, Any

from tc_messageBroker import RabbitMQ

from logger.hivemind_logger import logger


# def do_something(received_data):
#     A = 2 * 2
#     message = f"Calculation Results: {A}"
#     print(message)
#     print(f"received_data: {received_data}")

class EventBroker:
    rabbit_mq:RabbitMQ
    def __init__(self):
        self.rabbit_mq = None
        self.broker_url = os.getenv('RABBITMQ_HOST', "localhost")
        self.port = os.getenv('RABBITMQ_PORT', 5672)

        self.username = os.getenv('RABBITMQ_USER', "guest")
        self.password = os.getenv('RABBITMQ_PASS', "guest")
        logger.info(f"__init__ broker_url: {self.broker_url}:{self.port}")
        self.connect()

    def connect(self) -> RabbitMQ:
        if self.rabbit_mq is None:
            logger.info(f"broker_url: {self.broker_url}:{self.port}")

            self.rabbit_mq = RabbitMQ(
                broker_url=self.broker_url, port=self.port, username=self.username, password=self.password
            )

        return self.rabbit_mq

    async def a_listen(self, queue: str, event: str, callback: Callable):
        asyncio.get_event_loop().run_in_executor(None, self.listen, queue, event, callback)

    def listen(self, queue: str, event: str, callback: Callable):
        logger.debug("listening %s", queue)

        self.rabbit_mq.on_event(event, callback)

        # print("Waiting for messages...")
        self.rabbit_mq.connect(queue)
        print(f"Connected to {queue} queue!")

        self.rabbit_mq.consume(queue)
        print("consume messages...")
        if self.rabbit_mq.channel is not None:
            print("listening messages...")
            try:
                self.rabbit_mq.channel.start_consuming()
                print("Never reach here!")
            except KeyboardInterrupt:
                self.rabbit_mq.channel.stop_consuming()
                print("Disconnected from broker successfully!")
        else:
            print("Connection to broker was not successful!")

    def t_listen(self, queue: str, event: str, callback: Callable):
        logger.debug("listening %s", queue)

        self.rabbit_mq.on_event(event, callback)

        # print("Waiting for messages...")
        self.rabbit_mq.connect(queue)
        print(f"Connected to {queue} queue!")

        def consume_messages():
            self.rabbit_mq.consume(queue)
            print("consume messages...")
            if self.rabbit_mq.channel is not None:
                print("listening messages...")
                try:
                    self.rabbit_mq.channel.start_consuming()
                    print("Never reach here!")
                except KeyboardInterrupt:
                    self.rabbit_mq.channel.stop_consuming()
                    print("Disconnected from broker successfully!")
            else:
                print("Connection to broker was not successful!")

        # Create a separate thread to run the consume_messages function
        consume_thread = threading.Thread(target=consume_messages)
        consume_thread.start()
    async def a_publish(self, queue: str, event: str, content: dict[str, Any] | None):
        asyncio.get_event_loop().run_in_executor(None, self.publish, queue, event, content)

    def publish(self, queue: str, event: str, content: dict[str, Any] | None):
        logger.debug("publishing %s", content)

        self.rabbit_mq = RabbitMQ(
            broker_url=self.broker_url, port=self.port, username=self.username, password=self.password
        )

        self.rabbit_mq.connect(queue)

        if content is None:
            content = {"uuid": "d99a1490-fba6-11ed-b9a9-0d29e7612dp8", "data": "some results"}

        self.rabbit_mq.publish(
            queue,
            event=event,
            content=content,
        )
