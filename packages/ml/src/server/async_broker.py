import asyncio
import json

import aio_pika
import aio_pika.abc
from tc_messageBroker.rabbit_mq.event import Event
from tc_messageBroker.rabbit_mq.queue import Queue

from logger.hivemind_logger import logger
import utils.constants as constants

class AsyncBrokerQueue:
    def __init__(self, queue_name="HIVEMIND_API"):
        self.queue_name = queue_name
        self.events = {}

    def events_callback(self, json_message):
        _event_name = json_message['event']
        logger.debug(f"_event_name: {_event_name} self.events: {self.events}")
        if _event_name in self.events:
            cb = self.events[_event_name]
            if cb and callable(cb):
                cb(json_message, self.queue_name, _event_name)
            else:
                logger.debug(f"Callable callback or None {cb}")
        else:
            logger.debug(f"event_name not registered: {json_message}")

    async def listen(self, connection, event_name="RUN", callback=None):
        logger.debug(f"Listening {self.queue_name}->{event_name}")
        self.events[event_name] = callback
        await self.start(connection, queue_name=self.queue_name, callback=self.events_callback)

    async def start(self, connection, queue_name="HIVEMIND_API", callback=None):
        # logger.debug(f"Initialized Queue: {queue_name}")
        if connection is None:
            logger.error("Connection not initialized, did you call .connect()?")
        # await connection.__aenter__()
        # async with connection:
        # Creating channel
        channel: aio_pika.abc.AbstractRobustChannel = await connection.channel()

        # Declaring queue
        queue: aio_pika.abc.AbstractRobustQueue = await channel.declare_queue(
            queue_name,
            durable=True,
            auto_delete=False
        )

        try:
            async with queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                async for message in queue_iter:
                    async with message.process():
                        json_message = json.loads(message.body.decode())
                        # logger.debug(f"message.body: {json_message}")
                        if callback and callable(callback):
                            callback(json_message)
                        else:
                            logger.debug(f"Msg receive but not callback {json_message} {callback}")
                        # yield json_message
                        # if json_message['event'] == 'RUN':
            logger.debug(f"finished")
        except asyncio.CancelledError:
            logger.debug(f"Task for queue '{queue_name}' was canceled.")
        except Exception as e:
            logger.debug(f"An error occurred while processing queue '{queue_name}': {e}")


class AsyncBroker:
    def __init__(self):
        self.connection = None
        self.queues = {}

    async def connect(self):
        url = f"amqp://{constants.RABBITMQ_USER}:{constants.RABBITMQ_PASS}@{constants.RABBITMQ_HOST}/"
        logger.debug(f"Create connection to url: {url}")
        self.connection = await aio_pika.connect_robust(url=url) # TODO use constants.py

    async def listen(self, queue_name="HIVEMIND_API", event_name="RUN", callback=None):
        if queue_name not in self.queues:
            queue_obj = AsyncBrokerQueue(queue_name)
            self.queues[queue_name] = queue_obj

        queue_obj = self.queues[queue_name]

        if queue_obj:
            await queue_obj.listen(self.connection, event_name=event_name, callback=callback)
        else:
            logger.debug(f"queue_obj is none")