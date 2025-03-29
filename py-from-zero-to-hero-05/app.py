import logging

# Rest API
from flask import Flask, request

# LangChain
from langchain_ollama import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# DB Settings
from database import db
from model import Order

# Util
from util import create_chain, create_retriever, create_vector_db, internal_server_error_request, load_documents, bad_request, parse_order, not_found_request, ok_request, is_valid_scope, split_documents

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

# Context Memory using Python Dictionary
client_memories = {}  # chat
client_context = {}

# load documents from docs folder
logging.info("Loading documents...")
documents = load_documents("docs", "*.txt")

logging.info("Spliting documents in chunks...")
chuncks = split_documents(documents)

logging.info(f"Creating Vector DB {config_class.DB_COLLECTION_NAME} using model {config_class.AI_EMBEDDING_MODEL}...")
vector_db = create_vector_db(chuncks, config_class.AI_EMBEDDING_MODEL, config_class.DB_COLLECTION_NAME)

# chat section
logging.info(f"Initializing ollama model {config_class.AI_MODEL_NAME}...")
llm = ChatOllama(model=config_class.AI_MODEL_NAME
)

logging.info("Creating retriever...")
retriever = create_retriever(vector_db, llm)

logging.info("Preparing chain...")
chain = create_chain(retriever, llm)

logging.info("Done!")

@app.route('/info', methods=['POST'])
def ask():
   data = request.get_json()
   if not data or "client_id" not in data or "question" not in data:
       return bad_request("Invalid request. Missing fields: 'client_id' and 'question'.")

   client_id = str(data["client_id"])
   question = str(data["question"])

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

       # try to extract the order_id
      if not order_id and client_id in client_context:
         order_id = int(client_context[client_id])
      
      if not order_id:
         return bad_request("You need to provide the order number.")

      # Get order details
      order = Order.query.get(order_id)
      if order:
         # update context for that client_id
         client_context[client_id] = order_id
         return ok_request(order.to_string())
      else:
         return not_found_request(f"There is no purchase related to this number: {order_id}.")

   logging.info("info:validating scope...")
   scope_info = is_valid_scope(question, config_class.AI_MODEL_NAME)
   if scope_info.get("is_scoped") == False:
      return bad_request("We could not process your request. Try these topics: stores, products, purchases.")

   # is not about order, follow the flow
   logging.info("info:preparing buffer...")
   if client_id not in client_memories:
      client_memories[client_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
   memory = client_memories[client_id]
    
   # create chat using Retrieval (memory)
   logging.info("info:creating retrieval chain..")
   qa_chain = ConversationalRetrievalChain.from_llm(
      llm=llm,
      retriever=retriever,
      memory=memory
    )

   # run the user question
   logging.info("info:invoking question...")
   result = qa_chain.invoke({"question": question})
   answer = result.get("answer", "")

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