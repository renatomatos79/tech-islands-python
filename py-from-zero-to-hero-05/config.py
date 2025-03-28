import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base config"""
    APP_OPENAI_API_KEY = os.environ.get("APP_OPENAI_API_KEY", "")
    SECRET_KEY = os.environ.get("APP_SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI = os.environ.get("APP_DB_URL", "sqlite:///orders.db")
    PORT = os.environ.get("APP_PORT", 5000)
    # "gpt-4o", "gpt-3.5-turbo", "o3-mini", "o1-mini"
    AI_MODEL_NAME = "gpt-4o"

class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True

class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

## Current config
config_class = DevelopmentConfig if os.environ.get("APP_ENV") == "development" else ProductionConfig

# Set OpenAI Api_Key
os.environ["OPENAI_API_KEY"] = config_class.APP_OPENAI_API_KEY
