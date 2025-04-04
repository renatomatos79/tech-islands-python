import os
import logging
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
    OLLAMA_HOST = os.environ.get("APP_OLLAMA_HOST", "http://localhost:11434")
    SEMANTIC_SEARCH_THRESHOLD = 0.95
    DB_COLLECTION_NAME = "db-vector"
    DB_COLLECTION_PATH = os.environ.get("APP_DB_COLLECTION_PATH", "./chroma_db")
    RAG_DOCUMENT_FOLDER = os.environ.get("APP_RAG_DOC_FOLDER", "~/Desktop/renato-matos/cgi-python-adventure/py-from-zero-to-hero-06/docs")
    APP_REDIS_HOST=os.environ.get("APP_REDIS_HOST", "localhost")
    APP_REDIS_PORT=os.environ.get("APP_REDIS_PORT", "6379")

    @classmethod
    def print_config(cls):
        logging.basicConfig(level=logging.INFO)

        logging.info("... APP SETTINGS ...")
        logging.info("SECRET_KEY: {cls.SECRET_KEY}")
        logging.info("SQLALCHEMY_DATABASE_URI: {cls.SQLALCHEMY_DATABASE_URI}")
        logging.info("PORT: {cls.PORT}")
        logging.info("AI_MODEL_NAME: {cls.AI_MODEL_NAME}")
        logging.info("AI_EMBEDDING_MODEL: {cls.AI_EMBEDDING_MODEL}")
        logging.info("OLLAMA_HOST: {cls.OLLAMA_HOST}")
        logging.info("SEMANTIC_SEARCH_THRESHOLD: {cls.SEMANTIC_SEARCH_THRESHOLD}")
        logging.info("DB_COLLECTION_NAME: {cls.DB_COLLECTION_NAME}")
        logging.info("DB_COLLECTION_PATH: {cls.DB_COLLECTION_PATH}")
        logging.info("RAG_DOCUMENT_FOLDER: {cls.RAG_DOCUMENT_FOLDER}")

class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True

class ProductionConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

## Current config
config_class = DevelopmentConfig if os.environ.get("APP_ENV") == "development" else ProductionConfig


