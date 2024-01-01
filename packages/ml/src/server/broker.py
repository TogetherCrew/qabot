import asyncio
import logging
import threading
from typing import Callable, Any, Type, Union

from tc_messageBroker import RabbitMQ
from tc_messageBroker.rabbit_mq.event import Event
from tc_messageBroker.rabbit_mq.queue import Queue
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
        self.broker_url = constants.RABBITMQ_HOST
        self.port = constants.RABBITMQ_PORT
        self.username = constants.RABBITMQ_USER
        self.password = constants.RABBITMQ_PASS

        logger.info(f"__init__ broker_url: {self.broker_url}:{self.port}")
        self.rmq_consume = RabbitMQ(
            broker_url=self.broker_url,
            port=self.port,
            username=self.username,
            password=self.password,
        )

        self.rmq_publish = RabbitMQ(
            broker_url=self.broker_url,
            port=self.port,
            username=self.username,
            password=self.password,
        )

    @staticmethod
    def get_queue_by_event(string_to_find: str):
        member_mapping = {}
        for cls in (
            Event,
            Events.BotBaseEvent,
            Events.AnalyzerBaseEvent,
            Events.ServerEvent,
            Events.DiscordBotEvent,
            # Events.DiscordAnalyzerEvent, Events.HivemindEvent):  # if there not UNIQUE events across all classes that will get the last one
            Events.DiscordAnalyzerEvent,
        ):  # if there not UNIQUE events across all classes that will get the last one
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

    async def listen(self, queue: str, event: str, callback: Callable):
        logger.debug("listening %s", queue)

        async def job(queue: str, event: str, callback: Callable):
            await self.rmq_consume.on_event_async(event, callback)

            # print("Waiting for messages...")
            await self.rmq_consume.connect_async(queue)
            print(f"Connected to {queue} queue!")

            await self.rmq_consume.consume_async(queue)
            print("consume messages...")
            if self.rmq_consume.channel is not None:
                print("listening messages...")
                try:
                    self.rmq_consume.channel.start_consuming()
                    print("Never reach here!")
                except KeyboardInterrupt:
                    self.rmq_consume.channel.stop_consuming()
                    print("Disconnected from broker successfully!")
            else:
                print("Connection to broker was not successful!")

        threading.Thread(
            target=asyncio.run, args=(job(queue, event, callback),)
        ).start()

    async def add_event(self, event: str, callback: Callable):
        await self.rmq_consume.on_event_async(event, callback)

    async def publish(self, queue: str, event: str, content: dict[str, Any] | None):
        logger.debug("publishing %s", content)

        await self.rmq_publish.connect_async(queue)

        if content is None:
            content = {
                "uuid": "d99a1490-fba6-11ed-b9a9-0d29e7612dp8",
                "data": "some results",
            }

        await self.rmq_publish.publish_async(
            queue,
            event=event,
            content=content,
        )

    async def close(self):
        self.rmq_consume.connection.close()
        self.rmq_publish.connection.close()
