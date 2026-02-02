FROM python:3.12-slim

WORKDIR /app
RUN pip install -U uv

COPY . /app

EXPOSE 80

CMD ["uv","run","--with","mcp[cli]","--with","requests","mcp","run","main.py"]
