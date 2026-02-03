# Are you still using `pip`? Move to `uv`

Docs: https://docs.astral.sh/uv/

## Comparisons

### `uv` vs `nvm` (Node Version Manager)

**Similarities**
- Manages language versions
- Lets you install multiple versions
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

Into the MCP world we have some specific notations that need to be understood before going to dive into the code.
Let´s try to breakdown the basic MCP concepts using these topics:
- MCP Server (toolbox or capability provider)
- MCP Client (protocol translator)
- Protocols
- Mental Model
- Host

In order to better understand these actos/players we are going to build a toolbox and connect them with Microsoft Copilot.

But if you really want to go diving into the MCP world let me share the official github repo
- https://github.com/modelcontextprotocol


## MCP Server
MCP Server is not a HOST, a physical server, machine, with memory, CPU, on so.
An application you build and control that exposes capabilities to AI assistants.

Considering the role into the chain (I consider this piece into the game as most important one)
The MCP Server owns the tools, data, and logic.
Doing a comparison, it´s similar to:
- a microservice
- an API backend
- or a plugin server

Attention
But its interface is standardized by MCP, not by REST or gRPC.

What it contains
Inside an MCP server we usually have:
- Tools (functions the AI can call)
- Resources (readable data)
- Prompts (predefined system instructions)
- Business logic
- Databases, APIs, files, etc.

For this challenge, our MCP Server provides tools like (where tools live inside the MCP Server):
- customers_search
- customers_get_by_id
- customers_search_by_names
- customer_orders_by_status
- orders_get_by_status
- orders_get_by_customer_id

How communicates is handled into the MCP? It talks MCP over a transport such as:
- stdio (local process)
- HTTP (your localhost:8000/mcp)
- WebSockets, etc.

## MCP Client (polyglote - protocol translator)
What it is? The MCP Client is a software layer that understands the MCP protocol and knows how to:
- discover tools
- call tools
- send requests
- receive responses
- handle streaming, errors, etc.

Do we need to implement this protocol?
It is embedded inside tools like:
- VS Code Copilot
- Claude Desktop
- Cline
- Continue
- MCP Inspector

These apps contain an MCP Client internally.
We are going to play with these two clients: 
- VS Code Copilot 
- MCP Inspector (used to validate our tool)

Again, doing a simple analogy
Let´s consider "MCP" like a HTTP protocol.
- MCP Server = this is going to be our backend API
- MCP Client = Postman / fetch library / HTTP client

## Tools - “The verbs of the system”
Tools are functions exposed by the MCP server that the AI can call.
But do not see a tool like:
- the host
- the client
- the LLM

Tools are most like capabilities.
A tool is basically “Something the AI can ask our server to do.”

In out challenge, tools are like methods, endpoints and we have this specific notation for them

```python
@mcp.tool()
def customers_search(ids: List[int] = []) -> List[Dict]:
```

Each tool has:
- a name
- a description
- an input schema
- an output


Therefore "Tools" are verbs the "AI" can perform in your system.

Tool	                      What it lets the AI do
customers_search	          Read customers
customers_get_by_id	        Fetch one customer
customers_search_by_names	  Search by name
customer_orders_by_status	  Fetch orders

## Host “Where the AI lives and runs”
No, no, no.. hosts are not a physical machine, server, application server, virtual environment, nothing like that.
The Host is the application that runs the LLM and decides when to use tools.
What?
Yeah, consider the host like the software that we use to type our queries, ask AI do do something like these ones:
- VS Code Copilot Chat
- Claude Desktop
- Cursor
- Cline
- Continue
- MCP Inspector

So, what are hosts really doing?
- embeds the MCP Client
- embeds an LLM (Claude, GPT, Copilot, etc.)
- decides how the user interacts with tools

## What MCP transports actually are
We can understand "Transport" the way that language travels between client and server

### The first transport - STDIO (standard input/output)
This is a good choice for local process
The MCP server is launched as a local process, and communication happens over:
- stdin
- stdout

No HTTP, no ports, no URLs.

Who uses this protocol? 
- Claude Desktop (when triggering local tools)
- Many CLI-based MCP tools
- Some VS Code extensions

So, Instead of a URL, the host runs something like:

```python
python my_mcp_server.py
```

and then talks to it through pipes. 

When should we use STDIO?
Unless our MCP server runs on the same machine as the host and we do not need network access
Something when we want:
- simplicity
- speed
- no authentication
- no ports
- Local dev tools
- Personal automation
- Desktop integrations

**Pros 👍**
Very reliable locally
No CORS, no TLS, no firewall
Easy for dev tools

**Cons 👎**
Cannot work across machines
Cannot easily run inside cloud containers for multiple users
Harder to scale or share

### Second one - Streamable HTTP (recommended modern transport)
We are going to use this one triggering our tools using this endpoint
This is what you are goint to use use during our integration invoking requests against 

```python
http://localhost:8000/mcp
```

Another words, we can say, this is a single HTTP endpoint that behaves like a long-lived stream of messages between client and server.
- HTTP-based
- Bidirectional
- Streaming-friendly

When should you use Streamable HTTP?

- MCP server is in Docker (this is what we are going to build here in this challenge)
- We want to deploy it
- We want multiple hosts to use it
- We want cloud access
- We want real security (TLS, OAuth, API keys, etc.)
- Team-shared MCP servers
- Production systems
- Company tools

**Pros 👍**
Perfect for containers and microservices
Works great behind reverse proxies
Works over the internet
Scales well
Plays nicely with Kubernetes, AWS, Azure, etc.

**Cons 👎**
We may need:
CORS
Authentication
HTTPS
Proper streaming config

### Finally, this one - SSE (Server-Sent Events) 
This is legacy and being phased out :( 
and it´s being replaced by Streamable HTTP.
There is nothing else to say, I think :)

### How everything works together (full flow)?
1. An user (me, you, another service) type a message in VS Code Copilot Chat “Get all pending orders and summarize by customer.”
2. Host (VS Code Copilot Chat) that chats with us. It reads your message and asks the LLM what to do
3. LLM inside the Host thinks “I need to call a tool.”
4. Host uses its MCP Client to call our tool

```python
customer_orders_by_status(status="pending")
```

5. our MCP Server executes the function and returns a JSON.
6. MCP Client sends the result back to the Host.
7. LLM processes the result and gives you a final answer in plain English.

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
So when you run dev, you’re actually launching extra infrastructure that happens to make everything “work” in Docker.


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