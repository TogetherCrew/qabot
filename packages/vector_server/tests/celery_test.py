from tasks import vector_task

from utils.constants import OPENAI_API_KEY, DB_CONNECTION_STR, DB_GUILD

# t = vector_task.dummy.delay()
t = vector_task.vector_store_update.delay('random-session',OPENAI_API_KEY,DB_CONNECTION_STR,DB_GUILD)
print(t.status)