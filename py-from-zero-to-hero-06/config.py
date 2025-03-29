import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Base config
    SECRET_KEY: internally used by Flask dufing app.config.from_object(config_class)
    AI_MODEL_NAME: model used for chatting
    AI_EMBEDDING_MODEL: model used for rag during embedding process
    """
    SECRET_KEY = os.environ.get("APP_SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI = os.environ.get("APP_DB_URL", "sqlite:///orders.db")
    PORT = os.environ.get("APP_PORT", 5001)
    AI_MODEL_NAME = "mistral:7b"
    AI_EMBEDDING_MODEL = "nomic-embed-text"
    DB_COLLECTION_NAME = "db-vector"
    DB_COLLECTION_PATH = "./chroma_db"

class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True

class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

## Current config
config_class = DevelopmentConfig if os.environ.get("APP_ENV") == "development" else ProductionConfig

