import logging
import os

from celery.app import Celery

from logger.embedding_logger import logger
from tasks.helper import set_status
from vectorstore import vector_store_data
from utils.constants import REDIS_URI

logging.getLogger("pika").setLevel(logging.WARNING)
logger.debug(f"REDIS_URI {REDIS_URI}")
celery = Celery('celery', broker=REDIS_URI, backend=REDIS_URI)
celery.config_from_object('tasks.celeryconfig')

celery.conf.env = os.environ

CELERY_HOSTNAME = f'celery@{celery.main}'

def count_actives() -> tuple[int, list]:
    active = celery.control.inspect().active()
    logger.info(f'active {active}')
    count = 0
    list_actives = []
    if active and CELERY_HOSTNAME in active:
        list_actives = active[CELERY_HOSTNAME]
        count = len(list_actives)

    return count, list_actives


def has_active_task_id(task_id):
    found = None
    active = celery.control.inspect().active()
    logger.info(f'active {active}')
    logger.info(CELERY_HOSTNAME)
    if CELERY_HOSTNAME in active and isinstance(active[CELERY_HOSTNAME], list):
        logger.info('inside 1')
        for task in active[CELERY_HOSTNAME]:
            logger.info(f'inside 2 {task} {task_id}')
            if 'id' in task and task['id'] == task_id:
                logger.info('inside 3')
                found = task
                break

    return found


def is_active_empty():
    count, _ = count_actives()
    return count == 0


def take_active_at(index=0):
    count, list_actives = count_actives()
    found = None
    if count > 0:
        found = list_actives[index]
    return found


@celery.task(bind=True)
def vector_store_update(self, session: str, openai_key: str, db_connection_str: str, db_guild: str,
                        dates: list[str] = None,
                        channels: list[str] = None,
                        index: int = -1):
    set_status(self)
    logger.debug(f"session {session}")
    logger.debug('Starting vector store update FROM celery')
    # OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD
    vector_store_data.main([openai_key, db_connection_str, db_guild, self, dates, channels, index])

    set_status(self, meta={'current': 'END'})


if __name__ == '__main__':
    celery.start()
