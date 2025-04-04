from flask import Blueprint, request
import logging

# util
from src.lib.cache import cache_query, get_redis_client, search_cache
from src.lib.prompt import get_ollama_client, is_valid_scope, parse_order, rag_query
from src.lib.util import bad_request, create_retriever, create_vector_db, internal_server_error_request, load_documents, not_found_request, ok_request, sanitize_input, split_documents

# Import the config class
from config import config_class

# Redis
import redis

# DB Models
from src.model.order_model import OrderModel

# Create a Blueprint for info route
info_bp = Blueprint("info_bp", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# get redis client instance
redis_client = get_redis_client(redis, config_class.APP_REDIS_HOST, int(config_class.APP_REDIS_PORT), 0)

# load documents from docs folder
logging.info(f"Loading documents...{config_class.RAG_DOCUMENT_FOLDER}")
documents = load_documents(config_class.RAG_DOCUMENT_FOLDER, "*.txt")

logging.info(f"Documents to index...{len(documents)}")

logging.info("Spliting documents in chunks...")
chuncks = split_documents(documents)

logging.info(f"Chuncks count: {len(chuncks)}")

logging.info(f"Creating Vector DB {config_class.DB_COLLECTION_NAME} using model {config_class.AI_EMBEDDING_MODEL}...")
vector_db = create_vector_db(chuncks, config_class.OLLAMA_HOST, config_class.AI_EMBEDDING_MODEL, config_class.DB_COLLECTION_NAME, config_class.DB_COLLECTION_PATH,)

# chat section
logging.info(f"Initializing ollama model {config_class.AI_MODEL_NAME}...")
llm = get_ollama_client(config_class.OLLAMA_HOST).chat(model=config_class.AI_MODEL_NAME, stream=False)

logging.info("Creating retriever...")
retriever = create_retriever(vector_db)

logging.info("Done!")

@info_bp.route('/info', methods=['POST'])
def ask():
   data = request.get_json()
   if not data or "client_id" not in data or "question" not in data:
       return bad_request("Invalid request. Missing fields: 'client_id' and 'question'.")

   # sanitize the input content, by swearing words from text input
   question = sanitize_input(str(data["question"]))
   logging.info("sanitize_input")
   logging.info(f" -- before: {str(data["question"])}")
   logging.info(f" -- after: {question}")

   cached = search_cache(config_class.OLLAMA_HOST, config_class.AI_EMBEDDING_MODEL, redis_client, question, config_class.SEMANTIC_SEARCH_THRESHOLD)
   if cached:
      return ok_request(cached.get("content"), cached.get("ttl"))

   # using LLM, try to extract the order_id
   logging.info("info:parsing order...")
   order_info = parse_order(config_class.OLLAMA_HOST, question, config_class.AI_MODEL_NAME)
   if not order_info:
      logging.info("info:parse_order failed :(")
      return internal_server_error_request("Ops! Something went wrong! Try again")

   # is this an order request? 
   if order_info.get("is_order"):
      logging.info("info:question is an order")
      order_id = int(order_info.get("order_id"))
      
      if not order_id:
         return bad_request("You need to provide the order number.")

      # Get order details
      order = OrderModel.query.get(order_id)
      if order:
         cache_query(config_class.OLLAMA_HOST, config_class.AI_EMBEDDING_MODEL, redis_client, question, order.to_string())
         return ok_request(order.to_string())
      else:
         content = f"There is no purchase related to this number: {order_id}."
         cache_query(config_class.OLLAMA_HOST, config_class.AI_EMBEDDING_MODEL, redis_client, question, content)
         return not_found_request(content)

   logging.info("info:validating scope...")
   scope_info = is_valid_scope(config_class.OLLAMA_HOST, question, config_class.AI_MODEL_NAME)
   if scope_info.get("is_scoped") == False:
      content = "We could not process your request. Try these topics: stores, products, purchases."
      cache_query(config_class.OLLAMA_HOST, config_class.AI_EMBEDDING_MODEL, redis_client, question, content)
      return bad_request(content)

   logging.info("info:running rag_query...")
   answer = rag_query(config_class.OLLAMA_HOST, config_class.AI_MODEL_NAME, retriever, question)

   logging.info("info:adding query to cache...")
   cache_query(config_class.OLLAMA_HOST, config_class.AI_EMBEDDING_MODEL, redis_client, question, answer)

   logging.info("info:complete")
   return ok_request(answer)