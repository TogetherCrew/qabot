import logging
import os

from celery.app import Celery

from logger.embedding_logger import logger
from server.broker import EventBroker
from tasks.helper import set_status
from vectorstore import vector_store_data

logging.getLogger("pika").setLevel(logging.WARNING)

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_url = os.getenv('CELERY_REDIS_URL', f"redis://{redis_host}:{redis_port}")

celery = Celery('celery', broker=redis_url, backend=redis_url)
celery.config_from_object('tasks.celeryconfig')

# from dotenv import load_dotenv
# load_dotenv(dotenv_path='tasks.env')

celery.conf.env = os.environ

logger.info(f"os.environ: {os.environ}")
logger.info(f"celery.conf().env: {celery.conf.env}")

CELERY_HOSTNAME = f'celery@{celery.main}'

es = EventBroker()


def count_actives():
    active = celery.control.inspect().active()
    logger.info(f'active {active}')
    return len(active[CELERY_HOSTNAME]) if active and CELERY_HOSTNAME in active else 0


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
    return count_actives() == 0


@celery.task(bind=True)
def vector_store_update(self, session: str, openai_key, db_connection_str, db_guild):
    set_status(self)
    # celery.control.app.conf.env
    es.publish("HIVEMIND_API", "UPDATED_STORE",
               {"uuid": session, "data": '/update', "status": "BEGIN"})

    # OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD
    vector_store_data.main([openai_key, db_connection_str, db_guild, self])

    set_status(self, meta={'current': 'END'})

    es.publish("HIVEMIND_API", "UPDATED_STORE",
               {"uuid": session, "data": '/update', "status": "ENDED"})


if __name__ == '__main__':
    celery.start()
