# Let´s build our LLM api
python -m src.app.py

# This project requires python 3.11
brew install python@3.11
python3.11 --version

### Installing REDIS
```
docker network create --driver bridge backend-bridge-network
docker run --restart unless-stopped --name redisserver -d --network=backend-bridge-network -p 6379:6379 redis
docker run -d --name redis-insight -p 8001:8001 --network=backend-bridge-network redis/redisinsight:latest
docker run -d --name redis-commander -p 8081:8081 --network=backend-bridge-network --env REDIS_HOSTS=local:host.docker.internal:6379 rediscommander/redis-commander:latest
```

### Building the image
```
docker build -t flask-app .
```

### Running Docker Ollama (11435)
```
docker run -d --name ollama \
    -p 11435:11434 \
    --network=backend-bridge-network \
    -v ollama:/root/.ollama \
    ollama/ollama
```

### Running Flask API (inside a container we must use internal ollama port number)
```
docker run -d --name flask-container \
  -p 8000:80 \
  --network=backend-bridge-network \
  -v "$(pwd):/host-storage" \
  -e APP_SECRET_KEY=super_key_123 \
  -e APP_DB_URL=sqlite:///dev_users.db \
  -e APP_OLLAMA_HOST=http://ollama:11434 \
  -e APP_DB_COLLECTION_PATH=/host-storage/chroma_db \
  -e APP_RAG_DOC_FOLDER=/host-storage/docs \
  -e APP_REDIS_HOST=redisserver \
  -e APP_REDIS_PORT=6379 \
  -e APP_ENV=production \
  flask-app
```
