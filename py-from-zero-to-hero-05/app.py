# Rest API
from flask import Flask, request, jsonify

# LangChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# DB Settings
from database import db
from model import Order

# Util
from util import load_documents, bad_request, parse_order, not_found_request, ok_request, is_valid_scope

# Import the config class
from config import config_class

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

# load documents using documents folder
documents = load_documents("docs", "*.txt")

# Uses FAISS to create the vectorstore
embeddings = OpenAIEmbeddings()

vectorstore = FAISS.from_documents(documents, embeddings)

# Bootstrap chat
# temperature zero = precisely answers
chat = ChatOpenAI(model=config_class.AI_MODEL_NAME, temperature=0)

# Create retriever using vectorstore
retriever = vectorstore.as_retriever()

@app.route('/info', methods=['POST'])
def ask():
    data = request.get_json()
    if not data or "client_id" not in data or "question" not in data:
       return bad_request("Invalid request. Missing fields: 'client_id' and 'question'.")

    client_id = str(data["client_id"])
    question = str(data["question"])

    # using LLM, try to extract the order_id
    order_info = parse_order(chat, question)
    if order_info.get("is_order"):
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

    scope_info = is_valid_scope(chat, question)
    if scope_info.get("is_scoped") == False:
       return bad_request("We could not process your request. Try these topics: stores, products, purchases.")

    # is not about order, follow the flow
    if client_id not in client_memories:
       client_memories[client_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    memory = client_memories[client_id]
    
    # create chat using Retrieval (memory)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=chat,
        retriever=retriever,
        memory=memory
    )

    # run the user question
    result = qa_chain.invoke({"question": question})
    answer = result.get("answer", "")

    return ok_request(answer)

# Run the Flask App
if __name__ == '__main__':
   if config_class.DEBUG:
     app.run(debug=True, port=config_class.PORT)
   else:
     print(f"Running without debug mode PORT: {config_class.PORT}")
     from waitress import serve
     serve(app, host="0.0.0.0", port=config_class.PORT)