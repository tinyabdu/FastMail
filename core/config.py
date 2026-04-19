import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env(key: str, default=None, required: bool = False):
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value