# config/settings.py

import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from the .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    logger.warning(f".env file not found at {dotenv_path}")

class Settings:
    BASE_URL: str = os.getenv("BASE_URL")
    API_BASE_URL = os.getenv("API_BASE_URL")
    FIREBASE_SIGNIN_URL = os.getenv("FIREBASE_SIGNIN_URL")
    GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT")
    FT_EMAIL = os.getenv("FT_EMAIL")
    FT_PASSWORD = os.getenv("FT_PASSWORD")
    ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME")
    HEADLESS_MODE: str = os.getenv("HEADLESS_MODE", "true")  # ← Add this line

settings = Settings()