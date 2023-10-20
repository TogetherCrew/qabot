# Define the default values
import os

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings

from logger.hivemind_logger import logger

ENV = os.getenv('ENV')
print(f"ENV:{ENV}")
if ENV == 'local':
    load_dotenv(dotenv_path='../.local.env')
else:
    load_dotenv()

ACTIVELOOP_TOKEN = os.getenv("ACTIVELOOP_TOKEN", None)
# os.environ['ACTIVELOOP_TOKEN'] = ACTIVELOOP_TOKEN

OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")
assert OPENAI_API_MODEL, "OPENAI_API_MODEL environment variable is missing from .env"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
assert OPENAI_API_KEY, "OPENAI_API_KEY environment variable is missing from .env"
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
assert GOOGLE_CSE_ID, "GOOGLE_CSE_ID environment variable is missing from .env"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


#MongoDB
DB_CONNECTION_STR = os.getenv("DB_CONNECTION_STR", "")
assert DB_CONNECTION_STR, "DB_CONNECTION_STR environment variable is missing from .env"
DB_GUILD = os.getenv("DB_GUILD", "")
assert DB_GUILD, "DB_GUILD environment variable is missing from .env"


# Set Agent Settings
AGENT_NAME = os.getenv("AGENT_NAME", "")
assert AGENT_NAME, "AGENT_NAME variable is missing from .env"
AGENT_ROLE = os.getenv("AGENT_ROLE", "")
assert AGENT_ROLE, "AGENT_ROLE variable is missing from .env"
AGENT_OBJECTIVE = os.getenv("AGENT_OBJECTIVE", "")
assert AGENT_OBJECTIVE, "AGENT_OBJECTIVE variable is missing from .env"

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")


USE_HF_EMBEDDINGS = False
USE_LOCAL_STORAGE = True

DEFAULT_AGENT_DIR = os.path.join(os.path.dirname(__file__), "../agent_data")
print(f"DEFAULT_AGENT_DIR: {DEFAULT_AGENT_DIR}")

DATASET_PATH_HUB = "hub://windholyghost/"

DATASET_STORAGE_PATH = DEFAULT_AGENT_DIR if USE_LOCAL_STORAGE else DATASET_PATH_HUB

if USE_HF_EMBEDDINGS:
    # DEFAULT_EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2",
    #                                            client=SentenceTransformer(device='cpu'))
    DEFAULT_EMBEDDINGS = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    DEEPLAKE_RAW_PATH = os.path.join("hf", "DeepLake_VectorStore_413_419_raw_messages_HF_v2")
    DEEPLAKE_SUMMARY_PATH = os.path.join("hf", "DeepLake_VectorStore_413_419_summaries_HF_v2")
else:
    DEFAULT_EMBEDDINGS = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    DEEPLAKE_RAW_PATH = os.path.join("openai", "DeepLake_VectorStore_414_419_raw_messages")
    DEEPLAKE_SUMMARY_PATH = os.path.join("openai", "DeepLake_VectorStore_414_419_summaries")

PERIODIC_MEMORY_DIR = os.path.join(DATASET_STORAGE_PATH, "periodic_memory")
SEMANTIC_MEMORY_DIR = os.path.join(DATASET_STORAGE_PATH, "semantic_memory")
EPISODIC_MEMORY_DIR = os.path.join(DATASET_STORAGE_PATH, "episodic_memory")

# Define the base path for the serialization
BASE_PATH_SERIALIZATION = os.path.join(DEFAULT_AGENT_DIR, "serialization")

print(f"BASE_PATH_SERIALIZATION: {BASE_PATH_SERIALIZATION}")