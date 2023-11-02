from logger.embedding_logger import logger

from utils.constants import OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD
from vectorstore import vector_store_data

# t = vector_task.dummy.delay()
logger.debug('Starting vector store update in celery')
logger.debug(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
logger.debug(f"DB_CONNECTION_STR: {DB_CONNECTION_STR}")
logger.debug(f"DB_GUILD: {DB_GUILD}")

# vector_store_data.main([openai_key, db_connection_str, db_guild, self])
vector_store_data.main([OPENAI_API_KEY,DB_CONNECTION_STR,DB_GUILD, None])