import json
import glob
import os

# langchain 
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ollama
from langchain_ollama import OllamaEmbeddings
from ollama import chat

# Rest API
from flask import jsonify

from model_info import OrderInfo, ScopeInfo


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

def create_vector_db(chunks, embedding_model, db_collection_name, db_collection_path):
    """ Using document chuncks, creates a vector DB """
    vector_db = Chroma.from_documents(
        persist_directory=db_collection_path,
        documents=chunks,
        embedding=OllamaEmbeddings(model=embedding_model),
        collection_name=db_collection_name,
    )
    return vector_db

def create_retriever(vector_db, llm):
    return vector_db.as_retriever()

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

def rag_query(model, retriever, user_query):
    # Step 1: Retrieve relevant documents
    docs = retriever.get_relevant_documents(user_query)
    
    # Step 2: Concatenate them into a context string
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Step 3: Create a prompt with the context
    prompt = (
        f"Use the following context to answer the question:\n\n"
        f"{context}\n\n"
        f"Question: {user_query}"
    )
    
    # Step 4: Call Ollama chat
    response = chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.message.content

def parse_order(question, model):
    """ using LLM verifies if user request is related to an order """
    
    # Define the system and user prompt
    system_prompt = (
        "You are an assistant that analyzes questions to determine whether they refer to a purchase made on our e-commerce platform. "
        "If the question is about a purchase, return is_order as True and order_id that is an integer. "
        "If the question is not about an order, return is_order as False and order_id as None. "
        "Your response MUST be a valid JSON format. "
    )

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": question }
    ]

    # Run the chat
    response = chat(
        model=model, 
        messages=messages, 
        stream=False,
        format=OrderInfo.model_json_schema(),  # Use Pydantic to generate the schema or format=schema
        options={'temperature': 0},  # Make responses more deterministic
    )
    
    response_text = response.message.content.strip()
    is_order_info_response = OrderInfo.model_validate_json(response_text) 

    if is_order_info_response:
       return json.loads(response_text)
    
    # when it´s not a valid json
    return None

def is_valid_scope(question, model):
    """ using LLM verifies if user request is valid """
    
    # Define the system and user prompt
    system_prompt = (
        "You are an assistant that analyzes questions to determine whether they refer to purchase made on our e-commerce platform. "
        "If the question is not about our store locations or event our product details, return is_scoped as False and also provide an empty answer for the question. "
        "However If the question is either about our store locations or event our product details, return is_scoped as True and also provide an answer for the user question. "
        "Your response MUST be a valid JSON format. "
    )

    messages = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": question }
    ]

    # Run the chat
    response = chat(
        model=model, 
        messages=messages, 
        stream=False,
        format=ScopeInfo.model_json_schema(),  # Use Pydantic to generate the schema or format=schema
        options={'temperature': 0},  # Make responses more deterministic
    )

    # Get response text
    response_text = response.message.content.strip()
    is_scoped_info_response = ScopeInfo.model_validate_json(response_text) 

    if is_scoped_info_response:
       return json.loads(response_text)
    
    # when it´s not a valid json
    return None

def bad_request(message):
    return jsonify({"error": message}), 400

def not_found_request(message):
    return jsonify({"error": message}), 404

def ok_request(message):
    return jsonify({"answer": message}), 200

def internal_server_error_request(message):
    return jsonify({"answer": message}), 500