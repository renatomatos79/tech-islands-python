# Challenge Overview: Buil a custom VS Code Extension using Ollama with qwen2.5-coder Model

## Comparison Table (Claude and Something like Claude - Claude-like :)
Feature	Claude	Best local equivalents
General reasoning	Opus	DeepSeek-R1
Developer tasks	Sonnet	Qwen 2.5 Coder
Balanced chat	Sonnet	Llama-3.1
Fast chat	Haiku	Mistral Nemo
Safety	Very high	Medium
Context window	Very large	Small–medium

## Running our two projects


Run Docker Ollama (port 11435):
```bash
docker run -d --name ollama \
  -p 11435:11434 \
  --network=backend-bridge-network \
  -v ollama:/root/.ollama \
  --cpus="4.0" \
  --memory="8g" \
  -e OLLAMA_NUM_PARALLEL=1 \
  -e OLLAMA_NUM_THREADS=4 \
  ollama/ollama
```

Pull the `qwen2.5-coder` model:
```bash
docker exec -it ollama bash
ollama pull qwen2.5-coder
```

Example output:
```text
root@9a9337640a8a:/# ollama pull qwen2.5-coder
pulling manifest 
pulling 60e05f210007: 100% ▕██████████████████████████████████████████████████████████▏ 4.7 GB                         
pulling 66b9ea09bd5b: 100% ▕██████████████████████████████████████████████████████████▏   68 B                         
pulling 1e65450c3067: 100% ▕██████████████████████████████████████████████████████████▏ 1.6 KB                         
pulling 832dd9e00a68: 100% ▕██████████████████████████████████████████████████████████▏  11 KB                         
pulling d9bb33f27869: 100% ▕██████████████████████████████████████████████████████████▏  487 B                         
verifying sha256 digest 
writing manifest 
success 
```

Check the model list:
```bash
ollama list
```

The output must contains `llava:7b` model

```bash
NAME                    ID              SIZE      MODIFIED           
qwen2.5-coder:latest    dae161e27b0e    4.7 GB    About a minute ago (\0/)
```

Lets confirm Ollama is ready to play using:
```bash
curl http://localhost:11435/api/tags
```

```bash
{"models":[{"name":"llava:latest","model":"llava:latest","modified_at":"2026-01-27T15:59:45.933695009Z","size":4733363377,"digest":"8dd30f6b0cb19f555f2c7a7ebda861449ea2cc76bf1f44e262931f45fc81d081","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama","clip"],"parameter_size":"7B","quantization_level":"Q4_0"}},{"name":"llama3.2:latest","model":"llama3.2:latest","modified_at":"2026-01-20T14:57:16.960827012Z","size":2019393189,"digest":"a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama"],"parameter_size":"3.2B","quantization_level":"Q4_K_M"}}]}%                               
```

Lets set some env variables 

```bash
export OLLAMA_URL=http://localhost:11435
export OLLAMA_MODEL=qwen2.5-coder
```

Ok, no more delays, running the app:

```bash
cd py-from-zero-to-hero-13
python3.11 -m venv vscodext
source vscodext/bin/activate
pip install -r ./src/api/requirements.txt
cd ./src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The output should be:

```bash
INFO:     Will watch for changes in these directories: ['/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-13/src/api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [59364] using WatchFiles
INFO:     Started server process [59366]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Our api must be available

```bash
curl http://localhost:8000/ping
```

with this output

```json
{"status":"ok"}
```

Validating our LLM

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "fix_errors",
    "language": "python",
    "code": "pint(x)"
  }'
```

with this output

```json
{"updated_code":"```python\nprint(x)\n```","notes":"Task 'fix_errors' applied by LLM."}
```

## Builkding the VS Code Extension

Installing nodejs

```bash
brew install node
```

Lets confirm everything is ok

```bash
node -v
v25.5.0

npm -11.8.0
11.8.0
```

Installing project dependencies

```bash
 cd py-from-zero-to-hero-13/src/vscode-extension
 npm install
```



