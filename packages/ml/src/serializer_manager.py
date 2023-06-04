import asyncio
import os
import aiofiles
import base58
import pickle

from typing import Any
from pydantic import BaseModel, Field


class SerializationManager(BaseModel):
    """Class for managing serialization and file I/O."""

    base_path: str = Field("", description="Base path for saving files")

    async def serialize_and_save(self, obj: Any, name: str):
        """Serialize an object and save it to a file with a base58-encoded name."""
        serialized_obj = pickle.dumps(obj)
        filename = base58.b58encode(name.encode()).decode()
        filepath = f"{self.base_path}/{filename}.pkl"
        try:
            await asyncio.to_thread(os.makedirs, self.base_path, exist_ok=True)
            async with aiofiles.open(filepath, "wb") as f:
                await f.write(serialized_obj)
        except IOError as e:
            print(f"Error serializing and saving object to file {filepath}: {e}")

    def load_and_deserialize(self, name: str) -> Any:
        """Load a serialized object from a file with a base58-encoded name and deserialize it."""
        filename = base58.b58encode(name.encode()).decode()
        filepath = f"{self.base_path}/{filename}.pkl"
        try:
            with open(filepath, "rb") as f:
                serialized_obj = f.read()
            obj = pickle.loads(serialized_obj)
            return obj
        except (FileNotFoundError, pickle.UnpicklingError):
            print(f"Error loading and deserializing object from file: {filename}")
            return None
