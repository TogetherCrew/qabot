import os
import time

import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from logs.discord_logger import logger

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(
    command_prefix='/',
    intents=intents,
    case_insensitive=True  # Commands aren't case-sensitive
)

bot.author_id = os.environ.get("AUTHOR_ID")
assert bot.author_id, "AUTHOR_ID not set"


@bot.event
async def on_ready():  # When the bot is ready
    logger.debug("I'm in")
    logger.debug(bot.user)  # Prints the bot's username and identifier
    try:
        synced = await bot.tree.sync()
        logger.debug(f"Commands Synced {len(synced)}")
    except Exception as e:
        logger.debug(e)


def log_event(msg: str, queue_name: str, event_name: str):
    logger.info(f"{queue_name}->{event_name}::{msg}")


class FinishAction(Exception):
    pass


@bot.tree.command(name=f"ask{'2' if os.environ.get('BOT', None) else ''}")
@app_commands.describe(question="Ask anything to Hivemind")
async def ask(inter: discord.Interaction, question: str):
    start_time = time.monotonic()
    await inter.response.send_message("Searching...", ephemeral=True)

    url = os.environ.get("HIVEMIND_URL", 'http://localhost:3333/ask')

    if not url:
        logger.error(f"Error on ask: Without URL")
        await inter.edit_original_response(content='We have a problem, try again later')
        return
    initial_question = f"Your question: {question}\n"
    logger.debug(initial_question)
    last_message = None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'question': question}) as response:
                logger.debug(response)
                start = time.time()
                # response.raise_for_status()
                async for chunk in response.content.iter_any():
                    answer = chunk.decode()
                    last_message = f"{initial_question}\n{answer}\n"
                    logger.debug(f"Answer: {round(time.time() - start, 1)}s after start: '{answer}'")
                    logger.debug(f"Msg sent: {last_message}")
                    await inter.edit_original_response(content=last_message)
                    #                Write some code as if last_message start with 'Final Answer:'
                    if answer and answer.startswith('Final Answer:'):
                        raise FinishAction()

    except FinishAction:
        logger.info(f"FinishAction")
        pass
    except Exception as e:
        logger.error(f"Error on ask {e}")
        last_message = 'We have a problem, try again later'
        import traceback
        traceback.print_exc()
    finally:
        if session:
            await session.close()

    elapsed_time = time.monotonic() - start_time
    if elapsed_time > 60:
        elapsed_time = elapsed_time / 60
        time_unit = "minutes"
    else:
        time_unit = "seconds"

    result_message = f"{last_message}\nAnswer took about {elapsed_time:.2f} {time_unit}!"
    logger.debug(f"Msg sent: {result_message}")
    await inter.edit_original_response(content=result_message)

token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)  # Starts the bot
