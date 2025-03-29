import json
import glob
import os

# langchain 
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ollama
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Rest API
from flask import jsonify


def load_documents(folder_path, extension):
    """ from a document folder, returns a list of documents considering the extension file """
    documents = []
    for filepath in glob.glob(os.path.join(folder_path, extension)):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            documents.append(Document(page_content=content, metadata={"source": filepath}))
    return documents

def split_documents(documents):
    """ Split documents into smaller chunks """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
    chunks = text_splitter.split_documents(documents)
    return chunks

def create_vector_db(chunks, embedding_model, db_collection_name):
    """ Using document chuncks, creates a vector DB """
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model=embedding_model),
        collection_name=db_collection_name,
    )
    return vector_db

def create_retriever(vector_db, llm):
    """Create a multi-query retriever."""
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
different versions of the given user question to retrieve relevant documents from
a vector database. By generating multiple perspectives on the user question, your
goal is to help the user overcome some of the limitations of the distance-based
similarity search. Provide these alternative questions separated by newlines.
Original question: {question}""",
    )

    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
    )
    return retriever

def create_chain(retriever, llm):
    """Create the chain"""
    # RAG prompt
    template = """Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

def parse_order(question, model):
    """ using LLM verifies if user request is related to an order """
    
    # Define the system and user prompt
    system_prompt = (
        "You are an assistant that analyzes questions to determine whether they refer to a purchase made on our e-commerce platform. "
        "If the question is about a purchase, extract the order number (an integer) if present and identify the type of inquiry, "
        "which can be: 'order status', 'order details', 'order date', 'order value'. "
        "If the question is not about an order, return is_order as false. "
        "Your response MUST be exclusively a valid JSON, without any additional text, in the following format: "
        '{"is_order": <true or false>, "order_id": <number or null> }.'
    )

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": question }
    ]

    # Run the chat
    llm = ChatOllama(model=model)
    response = llm.invoke(messages)

    # Get response text
    response_text = response.content.strip()
    print("parse_order::response_text", response_text)

    # Parse and validate JSON
    try:
        data = json.loads(response_text)
        print("parse_order::data", data)
        if (
            isinstance(data, dict)
            and "is_order" in data and isinstance(data["is_order"], bool)
            and "order_id" in data and (isinstance(data["order_id"], int) or data["order_id"] is None)
        ):
            return data
        else:
            raise ValueError("Invalid JSON structure")
    except json.JSONDecodeError:
        raise ValueError("Response is not valid JSON")


def is_valid_scope(question, model):
    """ using LLM verifies if user request is valid """
    
    # Define the system and user prompt
    system_prompt = (
        "You are an assistant that analyzes questions to determine whether they refer to purchase made on our e-commerce platform. "
        "If the question is not about our store locations or event our product details"
        "your response MUST be exclusively a valid JSON, without any additional text, in the following format: "
        '{"is_scoped": <true or false>, "answer": "<string>"}.'
    )

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": question }
    ]

    # Run the chat
    llm = ChatOllama(model=model)
    response = llm.invoke(messages)

    # Get response text
    response_text = response['message']['content'].strip()

    # Parse and validate JSON
    try:
        data = json.loads(response_text)
        if (
            isinstance(data, dict)
            and "is_scoped" in data and isinstance(data["is_scoped"], bool)
            and "answer" in data and (isinstance(data["answer"], str) or data["answer"] is None)
        ):
            return data
        else:
            raise ValueError("Invalid JSON structure")
    except json.JSONDecodeError:
        raise ValueError("Response is not valid JSON")

def bad_request(message):
    return jsonify({"error": message}), 400

def not_found_request(message):
    return jsonify({"error": message}), 404

def ok_request(message):
    return jsonify({"answer": message}), 200

def internal_server_error_request(message):
    return jsonify({"answer": message}), 500