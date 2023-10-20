# Define the default values
import os

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings

ENV = os.getenv('ENV')

if ENV == 'local':
    load_dotenv(dotenv_path='../.local.env')
else:
    load_dotenv()

OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")
assert OPENAI_API_MODEL, "OPENAI_API_MODEL environment variable is missing from .env"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
assert OPENAI_API_KEY, "OPENAI_API_KEY environment variable is missing from .env"

# Set Agent Settings
AGENT_NAME = os.getenv("AGENT_NAME", "")
assert AGENT_NAME, "AGENT_NAME variable is missing from .env"
AGENT_ROLE = os.getenv("AGENT_ROLE", "")
assert AGENT_ROLE, "AGENT_ROLE variable is missing from .env"
AGENT_OBJECTIVE = os.getenv("AGENT_OBJECTIVE", None)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")


DEFAULT_AGENT_DIR = os.path.join(os.path.dirname(__file__), "../agent_data")

DEFAULT_EMBEDDINGS = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Define the base path for the serialization
BASE_PATH_SERIALIZATION = os.path.join(DEFAULT_AGENT_DIR, "serialization")