import asyncio
import time

import aiohttp


async def make_request(session, url, question, headers):
    async with session.post(url, json={'question': question}, headers=headers) as response:
        print(response)
        start = time.time()
        # await response.raise_for_status()
        async for chunk in response.content.iter_any():
            print(f"Got result {round(time.time() - start, 1)}s after start: '{chunk.decode()}'")


async def main():
    url_dev_token = 'http://localhost:3333/dev_token'
    url_ask = 'http://localhost:3333/ask'
    async with aiohttp.ClientSession() as session:
        async with session.post(url_dev_token) as response:
            token = (await response.json())['access_token']
            print(token)
            headers = {'Authorization': f'Bearer {token}'}

        tasks = []
        for question in ['Who is Amin?', 'What is the time?', 'How is the weather?']:
            task = asyncio.create_task(make_request(session, url_ask, question, headers))
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
