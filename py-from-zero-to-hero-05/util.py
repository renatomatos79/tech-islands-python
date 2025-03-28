import json
import glob
import os

# Rest API
from flask import Flask, request, jsonify

from langchain.docstore.document import Document
from langchain.schema import SystemMessage, HumanMessage

# load document list from documents folder
def load_documents(folder_path, extension):
    documents = []
    for filepath in glob.glob(os.path.join(folder_path, extension)):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            documents.append(Document(page_content=content, metadata={"source": filepath}))
    return documents


# using LLM, from request "question" content, try to extract order_id
def parse_order(chat, question):
    system_prompt = (
        "You are an assistant that analyzes questions to determine whether they refer to a purchase made on our e-commerce platform. "
        "If the question is about a purchase, extract the order number (an integer) if present and identify the type of inquiry, "
        "which can be: 'order status', 'order details', 'order date', 'order value'. "
        "If the question is not about an order, return is_order as false. "
        "Your response MUST be exclusively a valid JSON, without any additional text, in the following format: "
        '{"is_order": <true or false>, "order_id": <number or null> }.'
    )
    human_prompt = f"Question: \"{question}\""
    response = chat([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
    response_content = response.content.strip()
    return json.loads(response_content)

# using LLM, from request "question" content, try to validate the scope
def is_valid_scope(chat, question):
    system_prompt = (
        "You are an assistant that analyzes questions to determine whether they refer to purchase made on our e-commerce platform. "
        "If the question is not about our store locations or event our product details"
        "your response MUST be exclusively a valid JSON, without any additional text, in the following format: "
        '{"is_scoped": <true or false>, "answer": "<string>"}.'
    )
    human_prompt = f"Question: \"{question}\""
    response = chat([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
    response_content = response.content.strip()
    return json.loads(response_content)

def bad_request(message):
    return jsonify({"error": message}), 400

def not_found_request(message):
    return jsonify({"error": message}), 404

def ok_request(message):
    return jsonify({"answer": message}), 200