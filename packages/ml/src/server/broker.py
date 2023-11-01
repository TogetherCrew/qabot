import asyncio
import logging
import os
import threading
from enum import Enum
from typing import Callable, Any, Type

from tc_messageBroker import RabbitMQ
from tc_messageBroker.rabbit_mq.event import Event
import tc_messageBroker.rabbit_mq.event.events_microservice as Events

from logger.hivemind_logger import logger

logging.getLogger("PIKA").setLevel(logging.WARNING)

from utils import constants


class QueueObj(Enum):
    SERVER_API = Event.SERVER_API
    DISCORD_BOT = Event.DISCORD_BOT
    DISCORD_ANALYZER = Event.DISCORD_ANALYZER
    TWITTER_BOT = Event.TWITTER_BOT
    TWITTER_ANALYZER = Event.TWITTER_ANALYZER

    # HIVEMIND = Event.HIVEMIND

    def queue(self):
        return self.name

    @property
    def event(self) -> Type[Event]:
        return self.value


class EventBroker:
    rabbit_mq: RabbitMQ

    def __init__(self):
        self.rabbit_mq = None
        self.broker_url = constants.RABBITMQ_HOST
        self.port = constants.RABBITMQ_PORT
        self.username = constants.RABBITMQ_USER
        self.password = constants.RABBITMQ_PASS

        logger.info(f"__init__ broker_url: {self.broker_url}:{self.port}")
        self.connect()

    @staticmethod
    def get_queue_by_event(string_to_find: str):
        member_mapping = {}
        for cls in (Event, Events.BotBaseEvent, Events.AnalyzerBaseEvent,
                    Events.ServerEvent, Events.DiscordBotEvent,
                    # Events.DiscordAnalyzerEvent, Events.HivemindEvent):  # if there not UNIQUE events across all classes that will get the last one
                    Events.DiscordAnalyzerEvent):  # if there not UNIQUE events across all classes that will get the last one
            for name, value in cls.__dict__.items():
                member_mapping[name] = cls
        # print(member_mapping)
        matching_member = member_mapping.get(string_to_find)
        # print(matching_member)
        _queue_found = None
        if matching_member:
            for key, _enum in QueueObj._member_map_.items():
                # print(key, _enum.value)
                if _enum.value == matching_member:
                    logger.debug(f"Found: '{string_to_find}' in '{key}' Queue")
                    _queue_found = key
                    break  # we trust event names are UNIQUE otherwise we will need go full loop and check if have duplicates
        else:
            logger.info("No matching member found.")

        return _queue_found

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

    def add_event(self, event: str, callback: Callable):
        self.rabbit_mq.on_event(event, callback)

    def t_listen(self, queue: str):
        logger.debug("listening %s", queue)

        # print("Waiting for messages...")

        def consume_messages():
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
