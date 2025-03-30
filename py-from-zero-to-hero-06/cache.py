import numpy as np
from langchain_ollama import OllamaEmbeddings

def embed_text(embedding_model, text):
    """ Helper: Encode a query into a vector """
    embed_model = OllamaEmbeddings(model=embedding_model)
    vec = embed_model.embed_query(text)
    return np.array(vec, dtype=np.float32)  # ensure NumPy array

# Cosine similarity function
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Helper: Store query, vector, and response
def cache_query(embedding_model, redis, query, response):
    vector = embed_text(embedding_model, query)
    key = f"semantic:{query}"

    # Save as bytes
    redis.hset(key, mapping={
        "response": response,
        "vector": vector.tobytes()
    })

# Helper: Search cache using cosine similarity
def search_cache(embedding_model, redis, query, threshold = 0.95):
    new_vec = embed_text(embedding_model, query)
    
    for key in redis.scan_iter("semantic:*"):
        stored_vec = np.frombuffer(redis.hget(key, "vector"), dtype=np.float32)
        sim = cosine_similarity(new_vec, stored_vec)
        
        if sim >= threshold:
            print(f"Cache hit! similarity={sim}")
            return redis.hget(key, "response").decode()

    return None