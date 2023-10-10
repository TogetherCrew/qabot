import asyncio
import json

import aio_pika
import aio_pika.abc


class AsyncBroker:
    _queues = {}
    def listen(self, queue_name="HIVEMIND_API"):
        if queue_name not in self._queues:
            self._queues[queue_name] = []

        if queue_name in self._queues:
            co_listen_queue = self._queues[queue_name]
        else:
            co_listen_queue = AsyncBroker.listen_queue(queue_name)
            self._queues[queue_name] = co_listen_queue

        # if co_listen_queue is not None:


    @staticmethod
    async def listen_queue(queue_name="HIVEMIND_API"):
        print(f"queue_name: {queue_name}")
        connection = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/")
        # await connection.__aenter__()
        async with connection:
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
                    print(f"iterator")
                    async for message in queue_iter:
                        print(f"message")
                        async with message.process():
                            json_message = json.loads(message.body.decode())
                            print(f"message.body: {json_message}")
                            yield json_message
                            # if json_message['event'] == 'RUN':
                print(f"finished")
            except asyncio.CancelledError:
                print(f"Task for queue '{queue_name}' was canceled.")
            except Exception as e:
                print(f"An error occurred while processing queue '{queue_name}': {e}")


async def main():
    coroutines = [listen_queue(), listen_queue(queue_name='SOME')]
    tasks = []
    try:
        tasks = await asyncio.gather(*coroutines)
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt here if needed.
        pass
    finally:
        # Clean up tasks and close connections.
        for task in tasks:
            if task:
                task.cancel()
        await asyncio.gather(*coroutines, return_exceptions=True)
        # await con.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
