
# Are you still using `pip`? From now, let´s move to `uv`
https://docs.astral.sh/uv/

### uv vs nvm (Node Version Manager)
Similarity:
Manages language versions
Lets you install multiple Python versions
Lets projects “pin” a version

Difference:
nvm only manages Node versions.
uv also manages packages, tools, virtual environments, and lockfiles.

### uv vs pip
Similarity:
Installs Python packages.
Reads requirements.txt.

Difference:
uv is much faster.
uv also handles Python versions and lockfiles.
pip alone cannot manage Python versions or tools.

### uv vs pipx
Similarity:
Installs CLI tools globally.
Isolates tools.

Difference:
pipx only installs tools.
uv installs tools and project dependencies and Python itself.

### uv vs Poetry / Pipenv
Similarity:
Uses pyproject.toml
Generates lockfiles
Manages virtual environments
Handles dependencies per project

Difference:
uv is significantly faster.
uv also manages Python versions and tools.
Poetry/Pipenv usually do not manage Python installations themselves.

### uv vs Java Ecosystem
Java Tool	Similar uv Capability
SDKMAN	uv python install (manage language versions)
Maven / Gradle	uv add, uv lock, pyproject.toml (dependency mgmt)
jEnv	uv python pin (project version pinning)
But uv merges SDKMAN + Maven + pipx into one CLI.
One-Sentence Summary
If someone asks:
“What is uv?”
A very accurate answer is:
“uv is an all-in-one Python environment manager — like nvm + pip + pipx + poetry combined, but faster.”

Mental Model Diagram
Python World Before uv
-----------------------
pyenv     -> Python versions
pip       -> packages
pipx      -> tools
venv      -> environments
poetry    -> lockfiles/projects

Python World With uv
---------------------
uv -> everything above
So yes — you can compare it to nvm or pipx, but it’s more correct to say:
uv is not equivalent to one tool; it replaces several.


## Installing UV (macOS)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# let´s confirm uv is properly installed
uv --version
uv 0.9.27 (b5797b2ab 2026-01-26)

```

## Managing Python versions
```bash
# installing the latest python version
uv python install

# installling a specific version
uv python install 3.12

# uninstall a specific versino
uv python uninstall 3.11

# set a specific python version for a given project.. 
# run this command into the project folder
uv python pin 3.12

# which version am I using?
uv run python --version
Python 3.14.2

# already installed versions
uv python list --only-installed
cpython-3.14.2-macos-aarch64-none     .local/bin/python3.14 -> .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
cpython-3.14.2-macos-aarch64-none     .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
cpython-3.11.14-macos-aarch64-none    /opt/homebrew/bin/python3.11 -> ../Cellar/python@3.11/3.11.14_1/bin/python3.11
cpython-3.9.6-macos-aarch64-none      /usr/bin/python3

# available versions to install, including old patch versions
uv python list --all-versions
cpython-3.15.0a5-macos-aarch64-none                 <download available>
cpython-3.15.0a5+freethreaded-macos-aarch64-none    <download available>
cpython-3.14.2-macos-aarch64-none                   .local/bin/python3.14 -> .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
cpython-3.14.2-macos-aarch64-none                   .local/share/uv/python/cpython-3.14.2-macos-aarch64-none/bin/python3.14
cpython-3.14.2+freethreaded-macos-aarch64-none      <download available>
....
```

## Init a new project
```bash
# init adds a new project create a new directory for it
uv init playground
cd playground
ls -la 
.python-version     # sets the project version (pin)
README.md           # doc file
main.py             # basic file structure
pyproject.toml      # package dependencies (similar to requirments.txt when using pip)

# adding new package
# when adding a package using uv we dont need to active the .venv 
# this is automaticaly done when using uv into the project directory
uv add requests

# .venv is auto created
 ls -la 
.python-version
.venv               # built internally by uv
README.md
main.py
pyproject.toml
uv.lock             # current installed package version..


# adding an specific package version
uv add "fastapi>=0.110"

# listing the file pyproject.toml 
cat pyproject.toml 
[project]
name = "playground"                         # project name
version = "0.1.0"                           # project version
description = "Add your description here"
readme = "README.md"                
requires-python = ">=3.14"                  # current python version
dependencies = [                            # our two dependencies
    "fastapi>=0.110",
    "requests>=2.32.5",
]

# when pyproject.toml is not sync with uv.lock file, we need to sync it using
uv sync
Resolved 15 packages in 11ms
Audited 14 packages in 2ms
renatomatos@PT-D144L6PXF0 playground % 

# if lock file is missing, we can add it using uv lock
uv lock

# running the project
uv run python main.py
Hello from playground!
```

## Adding tools (likewise pipx or node version manager "nvm")


```bash
# running the tool without install it
uvx ruff check .

# listing installed tools
uv tool list
No tools installed

# install ruff
# Tools installed with `uv tool install` are NOT project dependencies.
# Therefore, they do not go into `pyproject.toml`
uv tool install ruff

# we can tie the tool to the project (likewise a dev dependence similar to package.json when using npm i --save-dev)
uv add --dev ruff 
Resolved 16 packages in 195ms
Prepared 1 package in 387ms
Installed 1 package in 3ms
 + ruff==0.14.14

# so then, we can identify this dev dependency in our toml file
cat pyproject.toml

...
[dependency-groups]
dev = [
    "ruff>=0.14.14",
]

# listing installed tools (once more)
uv tool list        
ruff v0.14.14
- ruff

# remove ruff
uv tool uninstall ruff
```

MCP - Model Context Protocol
https://github.com/modelcontextprotocol

MCP Servers
https://github.com/modelcontextprotocol/servers

Community version for a playground
=> Community servers are untested and should be used at your own risk. They are not affiliated with or endorsed by Anthropic.

https://github.com/modelcontextprotocol/servers