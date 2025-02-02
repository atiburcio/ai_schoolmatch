"""Configuration management for the school matcher application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory
ROOT_DIR = Path(__file__).parent

# Load environment variables from .env file
load_dotenv(ROOT_DIR / ".env")

def get_openai_api_key() -> str:
    """Get the OpenAI API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found! Please set it in your .env file:\n"
            "OPENAI_API_KEY=your-api-key-here"
        )
    return api_key
