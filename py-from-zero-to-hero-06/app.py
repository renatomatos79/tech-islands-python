import logging

# Rest API
from flask import Flask, request

# LangChain
from ollama import chat

# DB Settings
from database import db
from model import Order

# Redis
import redis

# Util
from util import create_retriever, create_vector_db, internal_server_error_request, load_documents, bad_request, parse_order, not_found_request, ok_request, is_valid_scope, rag_query, split_documents
from cache import cache_query, search_cache

# Import the config class
from config import config_class

# Configure logging
logging.basicConfig(level=logging.INFO)

# Flask
app = Flask(__name__)

# Load configurations from config.py
app.config.from_object(config_class)

# Bind SQLAlchemy to Flask app
db.init_app(app)

# Initialize Database
with app.app_context():
   db.create_all()

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# load documents from docs folder
logging.info("Loading documents...")
documents = load_documents("docs", "*.txt")

logging.info("Spliting documents in chunks...")
chuncks = split_documents(documents)

logging.info(f"Creating Vector DB {config_class.DB_COLLECTION_NAME} using model {config_class.AI_EMBEDDING_MODEL}...")
vector_db = create_vector_db(chuncks, config_class.AI_EMBEDDING_MODEL, config_class.DB_COLLECTION_NAME, config_class.DB_COLLECTION_PATH,)

# chat section
logging.info(f"Initializing ollama model {config_class.AI_MODEL_NAME}...")
llm = chat(model=config_class.AI_MODEL_NAME, stream=False)

logging.info("Creating retriever...")
retriever = create_retriever(vector_db, llm)

logging.info("Done!")

@app.route('/info', methods=['POST'])
def ask():
   data = request.get_json()
   if not data or "client_id" not in data or "question" not in data:
       return bad_request("Invalid request. Missing fields: 'client_id' and 'question'.")

   question = str(data["question"])

   cached = search_cache(config_class.AI_EMBEDDING_MODEL, redis_client, question, config_class.SEMANTIC_SEARCH_THRESHOLD)
   if cached:
      return ok_request(cached)

   # using LLM, try to extract the order_id
   logging.info("info:parsing order...")
   order_info = parse_order(question, config_class.AI_MODEL_NAME)
   if isinstance(order_info, ValueError):
      logging.info("info:parse_order failed :(")
      return internal_server_error_request("Ops! Something went wrong! Try again")

   # is this an order request? 
   if order_info.get("is_order"):
      logging.info("info:question is an order")
      order_id = int(order_info.get("order_id"))
      
      if not order_id:
         return bad_request("You need to provide the order number.")

      # Get order details
      order = Order.query.get(order_id)
      if order:
         cache_query(config_class.AI_EMBEDDING_MODEL, redis_client, question, order.to_string())
         return ok_request(order.to_string())
      else:
         content = f"There is no purchase related to this number: {order_id}."
         cache_query(config_class.AI_EMBEDDING_MODEL, redis_client, question, content)
         return not_found_request(content)

   logging.info("info:validating scope...")
   scope_info = is_valid_scope(question, config_class.AI_MODEL_NAME)
   if scope_info.get("is_scoped") == False:
      content = "We could not process your request. Try these topics: stores, products, purchases."
      cache_query(config_class.AI_EMBEDDING_MODEL, redis_client, question, content)
      return bad_request(content)

   logging.info("info:running rag_query...")
   answer = rag_query(config_class.AI_MODEL_NAME, retriever, question)

   logging.info("info:adding query to cache...")
   cache_query(config_class.AI_EMBEDDING_MODEL, redis_client, question, answer)

   logging.info("info:complete")
   return ok_request(answer)

# Run the Flask App
if __name__ == '__main__':
   if config_class.DEBUG:
     app.run(debug=True, port=config_class.PORT)
   else:
     print(f"Running without debug mode PORT: {config_class.PORT}")
     from waitress import serve
     serve(app, host="0.0.0.0", port=config_class.PORT)