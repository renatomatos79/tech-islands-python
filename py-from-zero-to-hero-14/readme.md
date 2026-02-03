# Are you still using `pip`? Move to `uv`

Docs: https://docs.astral.sh/uv/

## Comparisons

### `uv` vs `nvm` (Node Version Manager)

**Similarities**
- Manages language versions
- Lets install multiple versions
- Lets projects pin a version

**Differences**
- `nvm` only manages Node versions.
- `uv` also manages packages, tools, virtual environments, and lockfiles.

### `uv` vs `pip`

**Similarities**
- Installs Python packages
- Reads `requirements.txt`

**Differences**
- `uv` is much faster.
- `uv` also handles Python versions and lockfiles.
- `pip` alone cannot manage Python versions or tools.

### `uv` vs `pipx`

**Similarities**
- Installs CLI tools globally
- Isolates tools

**Differences**
- `pipx` only installs tools.
- `uv` installs tools and project dependencies (and Python itself).

### `uv` vs Poetry / Pipenv

**Similarities**
- Uses `pyproject.toml`
- Generates lockfiles
- Manages virtual environments
- Handles dependencies per project

**Differences**
- `uv` is significantly faster.
- `uv` also manages Python versions and tools.
- Poetry/Pipenv usually do not manage Python installations themselves.

### `uv` vs the Java ecosystem

| Java tool | Similar `uv` capability |
| --- | --- |
| SDKMAN | `uv python install` (manage language versions) |
| Maven / Gradle | `uv add`, `uv lock`, `pyproject.toml` (dependency mgmt) |
| jEnv | `uv python pin` (project version pinning) |

`uv` merges SDKMAN + Maven + pipx into one CLI.

### One-sentence summary

Are you still getting confused “What is `uv`?”

> `uv` is an all-in-one Python environment manager — like `nvm` + `pip` + `pipx` + Poetry combined, but faster.

### Python world before `uv`

```
pyenv     -> Python versions
pip       -> packages
pipx      -> tools
venv      -> environments
poetry    -> lockfiles/projects
```

Python world with `uv`

```
uv -> everything above
```


## Installing `uv` (macOS)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# confirm uv is properly installed
uv --version
# uv 0.9.27 (b5797b2ab 2026-01-26)
```

## Managing Python versions

```bash
# install the latest Python version
uv python install

# install a specific version
uv python install 3.12

# uninstall a specific version
uv python uninstall 3.11

# set a specific Python version for a given project
# run this command inside the project folder
uv python pin 3.12

# which version am I using?
uv run python --version
# Python 3.14.2

# already installed versions
uv python list --only-installed
# cpython-3.14.2-macos-aarch64-none     .local/bin/python3.14 -> .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
# cpython-3.14.2-macos-aarch64-none     .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
# cpython-3.11.14-macos-aarch64-none    /opt/homebrew/bin/python3.11 -> ../Cellar/python@3.11/3.11.14_1/bin/python3.11
# cpython-3.9.6-macos-aarch64-none      /usr/bin/python3

# available versions to install, including old patch versions
uv python list --all-versions
# cpython-3.15.0a5-macos-aarch64-none                 <download available>
# cpython-3.15.0a5+freethreaded-macos-aarch64-none    <download available>
# cpython-3.14.2-macos-aarch64-none                   .local/bin/python3.14 -> .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
# cpython-3.14.2-macos-aarch64-none                   .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
# cpython-3.14.2+freethreaded-macos-aarch64-none      <download available>
# ...
```

## Initialize a new project

```bash
# init creates a new project directory
uv init playground
cd playground
ls -la
# .python-version     # sets the project version (pin)
# README.md           # doc file
# main.py             # basic file structure
# pyproject.toml      # package dependencies (like requirements.txt when using pip)

# add a new package
# when adding a package using uv we do not need to activate the .venv
# this is automatically done when using uv inside the project directory
uv add requests

# .venv is auto-created
ls -la
# .python-version
# .venv               # built internally by uv
# README.md
# main.py
# pyproject.toml
# uv.lock             # current installed package versions

# add a specific package version
uv add "fastapi>=0.110"

# view pyproject.toml
cat pyproject.toml
# [project]
# name = "playground"                         # project name
# version = "0.1.0"                           # project version
# description = "Add your description here"
# readme = "README.md"
# requires-python = ">=3.14"                  # current python version
# dependencies = [                            # our two dependencies
#     "fastapi>=0.110",
#     "requests>=2.32.5",
# ]

# when pyproject.toml is not in sync with uv.lock, sync it using
uv sync
# Resolved 15 packages in 11ms
# Audited 14 packages in 2ms

# if lock file is missing, add it using
uv lock

# run the project
uv run python main.py
# Hello from playground!
```

## Adding tools (like `pipx` or Node's `nvm`)

```bash
# run a tool without installing it
uvx ruff check .

# list installed tools
uv tool list
# No tools installed

# install ruff
# tools installed with `uv tool install` are NOT project dependencies
# therefore, they do not go into `pyproject.toml`
uv tool install ruff

# tie the tool to the project (like a dev dependency in npm)
uv add --dev ruff
# Resolved 16 packages in 195ms
# Prepared 1 package in 387ms
# Installed 1 package in 3ms
#  + ruff==0.14.14

# see the dev dependency in pyproject.toml
cat pyproject.toml
# ...
# [dependency-groups]
# dev = [
#     "ruff>=0.14.14",
# ]

# list installed tools (once more)
uv tool list
# ruff v0.14.14
# - ruff

# remove ruff
uv tool uninstall ruff
```

## MCP (Model Context Protocol) brief introduction

Before diving into the code, there are a few MCP concepts to get straight:
- MCP Server (a toolbox or capability provider)
- MCP Client (protocol translator)
- Protocols
- Mental Model
- Host

To make this concrete, we will build a toolbox and connect it with Microsoft Copilot.

If we want to go deeper, here is the official MCP repo:
- https://github.com/modelcontextprotocol

## MCP Server
An MCP Server is not a physical host or machine. It is an application we build and control that exposes capabilities to AI assistants.

In the chain, the MCP Server is the most important piece:
- It owns the tools, data, and logic.
- It´s similar to a microservice, API backend, or plugin server.

**Important:** 

The interface that allows the communication between server and client is standardized by MCP, not by REST or gRPC.

**What it contains**
- Tools (functions the AI can call)
- Resources (readable data)
- Prompts (predefined system instructions)
- Business logic
- Databases, APIs, files, etc.

For this challenge, our MCP Server provides tools like:
- customers_search
- customers_get_by_id
- customers_search_by_names
- customer_orders_by_status
- orders_get_by_status
- orders_get_by_customer_id

How communication works: it talks MCP over a transport such as:
- stdio (local process)
- HTTP (localhost:8000/mcp)
- WebSockets, etc.

## MCP Client (polyglot protocol translator)
The MCP Client is a software layer that understands MCP and knows how to:
- discover tools
- call tools
- send requests
- receive responses
- handle streaming, errors, etc.

Do we need to implement the protocol ourselves? No. It is embedded inside tools like:
- VS Code Copilot
- Claude Desktop
- Cline
- Continue
- MCP Inspector

Into the plauground folder, our MCP server is using these two clients:

- VS Code Copilot
- MCP Inspector (used to validate our tool)

**Analogy:** 

If we consider MCP like HTTP. So, then:
- MCP Server = backend API
- MCP Client = Postman / fetch library / HTTP client

## Tools - "The verbs of the system"
Tools are functions exposed by the MCP server that the AI can call. A tool is not:
- the host
- the client
- the LLM

Tools are capabilities: "something the AI can ask our server to do."

In our challenge, tools are like methods/endpoints with this following notation:

```python
@mcp.tool()
def customers_search(ids: List[int] = []) -> List[Dict]:
```

Each tool has:
- a name
- a description
- an input schema
- an output

So, tools are the verbs the AI can perform in your system.

| Tool | What it lets the AI do |
| --- | --- |
| customers_search | Read customers |
| customers_get_by_id | Fetch one customer |
| customers_search_by_names | Search by name |
| customer_orders_by_status | Fetch orders |

## Host "Where the AI lives and runs"
Hosts are not physical machines or servers. A host is the application that runs the LLM and decides when to use tools.

Examples:
- VS Code Copilot Chat
- Claude Desktop
- Cursor
- Cline
- Continue
- MCP Inspector

So, what does a host really do?
- embeds the MCP Client
- embeds an LLM (Claude, GPT, Copilot, etc.)
- decides how the user interacts with tools

## What MCP transports actually are
A "transport" is how messages travel between client and server.

### Transport 1 - STDIO (standard input/output)
This is a good choice for local processes. The MCP server is launched locally, and communication happens over:
- stdin
- stdout

No HTTP, no ports, no URLs.

Is there someone using this? Yeah, we have:
- Claude Desktop (when triggering local tools)
- Many CLI-based MCP tools
- Some VS Code extensions

Instead of a URL, the host runs something like:

```python
python my_mcp_server.py
```

When should we use STDIO?
- Same machine as the host
- No network access needed
- We want simplicity and speed
- No authentication or ports
- Local dev tools / personal automation / desktop integrations

**Pros**
- Very reliable locally
- No CORS, TLS, or firewall
- Easy for dev tools

**Cons**
- Cannot work across machines
- Hard to run in cloud containers for multiple users
- Harder to scale or share

### Transport 2 - Streamable HTTP (recommended modern transport)
We will use this transport via:

```python
http://localhost:8000/mcp
```

This is a single HTTP endpoint that behaves like a long-lived stream of messages between client and server:
- HTTP-based
- Bidirectional
- Streaming-friendly

When should we use Streamable HTTP?
- MCP server runs in Docker (what we built here! Really? Yeah, I give my word)
- We want to deploy it
- Multiple hosts need access
- We want cloud access
- We need real security (TLS, OAuth, API keys, etc.)
- Team-shared MCP servers
- Production systems
- Company tools

**Pros**
- Great for containers and microservices
- Works behind reverse proxies
- Works over the internet
- Scales well
- Plays nicely with Kubernetes, AWS, Azure, etc.

**Cons**
- We still may need: CORS, authentication, HTTPS, proper streaming config

### Transport 3 - SSE (Server-Sent Events)
This is legacy and being phased out; it is being replaced by Streamable HTTP.

### How everything works together (full flow)
1. A user types a message in VS Code Copilot Chat: "Get all pending orders and summarize by customer."
2. The Host reads the message and asks the LLM what to do.
3. The LLM thinks: "I need to call a tool."
4. The Host uses its MCP Client to call our tool:

```python
customer_orders_by_status(status="pending")
```

5. Our MCP Server executes the function and returns JSON.
6. The MCP Client sends the result back to the Host.
7. The LLM processes the result and gives a final answer in plain English.

## Time to code - Let´s start our playground


> Installing our tools

cd playground
uv sync
uv run mcp dev main.py


> build a docker image for our app
```bash
docker container rm random-names-mcp --force
docker build -t random-names-mcp .
```

Using DEV mode
```bash
docker run -d --name random-names-mcp \
  -p 8000:8000 -p 6274:6274 -p 6277:6277 \
  -e APP_PORT=8000 \
  -e MCP_MODE=dev \
  random-names-mcp
```

Prod mode
```bash
docker run -d --name random-names-mcp ^
  -p 8000:8000 ^
  -e APP_PORT=8000 ^
  -e MCP_MODE=run ^
  random-names-mcp
```

> running mcp using docker

```bash
docker mcp --help
docker mcp catalog init
docker mcp server enable playwright
docker mcp gateway run
```

## What mcp dev vs mcp run really means?

🔹 mcp run main.py
This means:
Start only your MCP server
- No Inspector
- No proxy
- No extra ports
Meant for production / containers / servers
Your FastMCP server should be reachable on:

```bash
APP_PORT = 8000
```

🔹 mcp dev main.py
This means:
Start three things inside the container:
- Our MCP server → port 8000
- MCP Inspector UI → port 6274
- MCP Proxy → port 6277

So when we run dev, you’re actually launching extra infrastructure that happens to make everything “work” in Docker.


## MCP Tool x Copilot

> Requesting orders by status
![alt text](./imgs/image.png)

> Combining Customer Data x Order Data
![alt text](./imgs/image-1.png)

> Json Response
```json
[
  {
    "order": {
      "orderDate": "2026-01-10T11:15:00Z",
      "orderValue": 24.9,
      "description": "Haircut + beard trim",
      "status": "done"
    },
    "customer": {
      "id": 1,
      "name": "Ana Silva",
      "countryCode": "PT"
    }
  },
  {
    "order": {
      "orderDate": "2026-01-22T09:05:00Z",
      "orderValue": 19.99,
      "description": "Haircut",
      "status": "done"
    },
    "customer": {
      "id": 2,
      "name": "Bruno Costa",
      "countryCode": "PT"
    }
  },
  {
    "order": {
      "orderDate": "2026-01-12T14:10:00Z",
      "orderValue": 29.5,
      "description": "Beard styling + wax",
      "status": "done"
    },
    "customer": {
      "id": 7,
      "name": "Giulia Rossi",
      "countryCode": "IT"
    }
  },
  {
    "order": {
      "orderDate": "2026-01-18T12:00:00Z",
      "orderValue": 22,
      "description": "Haircut + wash",
      "status": "done"
    },
    "customer": {
      "id": 9,
      "name": "Inês Almeida",
      "countryCode": "PT"
    }
  }
]
```
