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

## MCP (Model Context Protocol)

- https://github.com/modelcontextprotocol
- https://github.com/modelcontextprotocol/servers


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

## What mcp dev vs mcp run really mean

🔹 mcp run main.py
This means:
Start only your MCP server
✅ No Inspector
✅ No proxy
✅ No extra ports
Meant for production / containers / servers
Your FastMCP server should be reachable on:

```bash
APP_PORT = 8000
```

🔹 mcp dev main.py
This means:
Start three things inside the container:
✅ Your MCP server → port 8000
✅ MCP Inspector UI → port 6274
✅ MCP Proxy → port 6277
So when you run dev, you’re actually launching extra infrastructure that happens to make everything “work” in Docker.


Getting the TOKEN
```bash
init='{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": { "name": "curl-bash", "version": "1.0" }
  }
}'

curl -i -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$init"
```


Using the response token (Session ID)
```bash
curl -i -X POST http://localhost:8000/mcp \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: fdcb11c5a9b845cdb8004e3ca56300e7" \
  -H "MCP-Protocol-Version: 2024-11-05" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_random_name",
      "arguments": { "names": ["Renato", "Gabi", "Docker", "MCP"] }
    }
  }'
```