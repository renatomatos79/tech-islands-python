# Let´s build our LLM api
export PYTHONPATH=$PYTHONPATH:./src
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

### Running our container
```
docker run -d --name flask-container -p 8000:80 -e APP_SECRET_KEY=super_key_123 -e APP_DB_URL=sqlite:///dev_users.db -e APP_ENV=production flask-app
```
