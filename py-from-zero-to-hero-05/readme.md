# Let´s build our LLM api
# This project requires python 3.11
brew install python@3.11
python3.11 --version

### Installing Ollama
https://ollama.com/


### Ollama
```
Model defitiion, supported languages and use cases:
https://ollama.com/library/llama3.3

Benchmark table fields:
MMLU: massive, mult task language understanding - Tests general world knowledge across 57 tasks.
tests general knowledge across subjects (history, biology, law, etc.).

MMLU PRO: Harder version of MMLU with 5-shot context and chain-of-thought (CoT) prompting **
- 5-shot prompting: shows 5 examples before asking the model to solve a new one.
- CoT (Chain-of-Thought) prompting: encourages the model to explain its reasoning step by step before answering.


Example — Regular MMLU (0-shot)
Question (Psychology):

pgsql
Copy
Edit
Which of the following best describes classical conditioning?

A. A type of learning where behavior is controlled by consequences  
B. Learning through observation of others  
C. Learning through association of stimuli  
D. Problem-solving through trial and error

Expected model output:
C

MMLU PRO (5-shot + CoT)
Prompt includes 5 examples:
Q1: What is the capital of France?
A1: Let's think step-by-step. France is a European country. Its most famous city is Paris, which is also the capital. So the answer is: Paris

Q2: Who wrote the play "Romeo and Juliet"?
A2: Let's think. "Romeo and Juliet" is a classic tragedy written in the 16th century. The most well-known playwright from that time is William Shakespeare. So the answer is: William Shakespeare

...

Q6: Which of the following best describes classical conditioning?

A. A type of learning where behavior is controlled by consequences  
B. Learning through observation of others  
C. Learning through association of stimuli  
D. Problem-solving through trial and error

A6: Let's think step-by-step. Classical conditioning was first studied by Pavlov with dogs. It involves associating a neutral stimulus with a meaningful one. Over time, the neutral stimulus alone can trigger the response. This matches "learning through association of stimuli". So the answer is: C

Why MMLU PRO is hard?
The model needs to understand both subject matter and apply structured reasoning.

It simulates more realistic "assistant-style" answers (like ChatGPT or Llama in a real chat app).

Instruction Following
IFEval: Measures how well the model follows instructions.
MBPP EvalPlus: Similar but more beginner-friendly problems

Code:
HumanEval: Tests coding ability — can it solve real-world coding tasks?

MATH:
MATH benchmark: Tests math problem solving (0-shot with chain of thought).

Reasoning:
GPQA Diamond: Graduate-level reasoning questions.

Tool Use
BFCL v2: Evaluates model's ability to use APIs, tools, or function calls.

Long Context
NIH/Multi-needle: Tests performance with long documents.

Multilingual
Multilingual MGSM: Math reasoning in multiple languages.

Pricing
Cost to process 1 million tokens:

Type 	 Llama 3.3 	  GPT-4o
Input	    $ 0.10	   $2.50
Output	  $ 0.40	  $10.00

Understing model parameters
q4:
- q: Denotes quantization.​
- 4: Indicates a 4-bit quantization, meaning each weight in the model is represented using 4 bits.​
- k: Refers to the use of K-means clustering in the quantization process. K-means clustering helps in grouping similar weights, which can lead to better quantization with reduced precision loss.​
- m: Represents the medium variant within the K-means quantization methods. The variants typically include:​

Medium
s: Small​
m: Medium​
l: Large​

- context lenght: nunber of tokens (context window) model can process in a single input
https://platform.openai.com/tokenizer

- embedding lenght: This is the dimension of the embedding vectors produced by the model for each token.
More expressive representations (better understanding of relationships) 

- quantitization: 
<4k: Super fast, barely touches RAM.
8k:	 Standard use, excellent performance.
16k: Still solid on most modern CPUs (e.g., M1/M2, Ryzen 7).
32k: Possible with more RAM (16GB+), expect slower response time.
65k – 131k:	You’ll need at least 32–64 GB RAM and may need llama.cpp with patched support. Only needed for advanced RAG or document summarization tasks.
```

### Most important Ollama Command Line
- ollama help
- ollama pull : download the model
- ollama list : available local models
- ollama rm llama3.2:1b
- ollama run codegema:2b
- ollama -bye to leave editor

### Customizing model using Modelfile
1. Create a file named Modelfile
2. Add this content to the file
FROM llama3.2
PARAMETER temperature 1 
SYSTEM """
You are Renato, a very funny assistant who answers questions using a joke style
"""
3. ollama create renato-model-llama -f ./Modelfile
4. ollama list
5. ollama run renato-model.llama
What is your name? My name is Renato.

### Most important Ollama API
default port is 11434
who is using 11434?
´´´
lsof -i :11434
´´´



### Important notes about SDK Reference
https://python.langchain.com/v0.2/api_reference/ollama/chat_models/langchain_ollama.chat_models.ChatOllama.html

### Add a new folder "py-from-zero-to-hero-05"
```
mkdir py-from-zero-to-hero-05
cd py-from-zero-to-hero-05
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
