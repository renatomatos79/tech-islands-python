# Let´s build our LLM api

### Add a new folder "py-from-zero-to-hero-03"
```
mkdir py-from-zero-to-hero-03
cd py-from-zero-to-hero-03
```

### So, then let´s build a dynamic environment named "llmapi"
```
python -m venv llmapi
```

### And activate our new dynamic env "llmapi"
```
.\llmapi\Scripts\activate
```

### Rather than installing packages one by one, let´s use our dependencies file :)
```
pip install -r .\requirements.txt
```

### Finally, we should confirm whether our packages were properly installed
```
pip list
```

# (1) Building a LLM API

### (1.1) Env file

In order to avoid hardcoded content into our LLM API, we are going to build an .env file 
providing these five variables instead.

- APP_OPENAI_API_KEY=your OpenAI API Key
  Open https://platform.openai.com/api-keys and add a new secret key

- APP_SECRET_KEY: 
  The SECRET_KEY is used to generate secure CSRF tokens
  encrypts and signs the session cookies to prevent tampering
  required to sign JSON Web Tokens (JWTs) which also prevents unauthorized modifications of JWT tokens

- APP_DB_URL:
  Connection string used to bind database  

- APP_ENV:
  Identify current env (development or production) 

- APP_PORT: 
  Customise API port number
 
```
APP_OPENAI_API_KEY=type-your-open-ai-api-key
APP_SECRET_KEY=super_secure_random_key_123
APP_DB_URL=sqlite:///dev_users.db
APP_ENV=development
APP_PORT=8000
```

### (1.2) Config file

This configuration file is very similar, <br> 
but I want to highlight this line where we set the environment variable OPENAI_API_KEY, <br> 
which is intended for making requests to our AI model.

```
# Set OpenAI Api_Key
os.environ["OPENAI_API_KEY"] = config_class.APP_OPENAI_API_KEY
```

### (1.3) Setup database

Create a database.py file using the code right below using a detached (not related to Flask APP) db instance

```
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (without Flask app)
db = SQLAlchemy()
```

### (1.4) Add a file named model.py

This file is used to map our order table fields
- id
- customer_id
- order_date
- order_status
- order_value

```
class Order(db.Model):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    order_date = Column(Date, nullable=False)
    # A: Active, C: Cancelled, D: Done
    order_status = Column(String(1), nullable=False)
    order_value = Column(Numeric(15,2), nullable=False)
```

### (1.5) Add a file named util.py

We will use this file to reuse the following common functions:
- load_documents: Loads files from disk and converts them into langchain.docstore.document.Document objects.
- parse_order: Utilizes the LLM to extract the order_id as an alternative to regex.
- is_valid_scope: Validates the user's question scope to prevent consuming model credits on out-of-scope content.
- bad_request: Returns an HTTP response for a 400 Bad Request status.
- not_found_request: Returns an HTTP response for a 404 Not Found status.
- ok_request: Provides an HTTP response for a 200 OK status.

### (1.6) Finally, add a file named app.py

Let me underline these packages and LLM methods: <br>

#### OpenAIEmbeddings:
This is used to generate vector embeddings for text using OpenAI's embedding models <br>
which are commonly used for semantic search, retrieval-augmented generation (RAG), and vector database queries.

#### FAISS:
refers to LangChain's integration with FAISS (Facebook AI Similarity Search), <br> 
which is an efficient vector search library used for storing, indexing, and searching high-dimensional embeddings.

```
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OpenAIEmbeddings()
documents = load_documents("docs", "*.txt")
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()
```

Attention! <br>
The retriever in responsible for fetching relevant documents based on the similarity <br>
of their embeddings to a given query. It is commonly used in Retrieval-Augmented Generation (RAG) <br>
systems to enhance AI responses with contextual information. 

#### ChatOpenAI:
This is a wrapper for OpenAI's chat models  (like gpt-3.5-turbo and gpt-4), <br>
which provides an interface to interact with OpenAI’s chat-based models in LangChain.

<b>temperature</b> parameter:
- Lower values (e.g., 0) make the model more deterministic, <br> 
  meaning it will produce the same response for the same input
- Higher values (e.g., 1.0 or more) increase the randomness, <br> 
  making the responses more diverse and creative.

```
chat = ChatOpenAI(model=config_class.AI_MODEL_NAME, temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever, memory=memory)
result = qa_chain.invoke({"question": question})
answer = result.get("answer", "")
```

Attention! <br>
- ConversationalRetrievalChain.from_llm: is part of LangChain and is used to build a question-answering system <br>
that retrieves relevant documents from a vector database and maintains conversation history.
- ConversationBufferMemory: stores conversation history, so the model can maintain context across multiple queries.

### (1.7) Running the app
```
python app.py
```

### So, let's run a quick demo to showcase what we've accomplished so far.
<p align="center">
  <img src="https://github.com/renatomatos79/cgi-python-adventure/blob/main/images/demo-openai-llm.gif" height="400px" width="100%" alt="LLM API Demo">
</p>
