# Define the default values
import os

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
# from sentence_transformers import SentenceTransformer



# Set API Keys
load_dotenv()

ACTIVELOOP_TOKEN = os.getenv("ACTIVELOOP_TOKEN", None)
os.environ['ACTIVELOOP_TOKEN'] = ACTIVELOOP_TOKEN

OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo-0613")
assert OPENAI_API_MODEL, "OPENAI_API_MODEL environment variable is missing from .env"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
assert OPENAI_API_KEY, "OPENAI_API_KEY environment variable is missing from .env"


#MongoDB
DB_CONNECTION_STR = os.getenv("DB_CONNECTION_STR", "")
assert DB_CONNECTION_STR, "DB_CONNECTION_STR environment variable is missing from .env"
DB_GUILD = os.getenv("DB_GUILD", "")
assert DB_GUILD, "DB_GUILD environment variable is missing from .env"

USE_LOCAL_STORAGE = True

DATASET_PATH_HUB = "hub://windholyghost/"

DEEPLAKE_FOLDER = "vector_store"

# DATASET_STORAGE_PATH = DEFAULT_AGENT_DIR if USE_LOCAL_STORAGE else DATASET_PATH_HUB

DEFAULT_EMBEDDINGS = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

DEEPLAKE_RAW_PATH = os.path.join(DEEPLAKE_FOLDER, "DeepLake_VectorStore_414_419_raw_messages")
DEEPLAKE_SUMMARY_PATH = os.path.join(DEEPLAKE_FOLDER, "DeepLake_VectorStore_414_419_summaries")
