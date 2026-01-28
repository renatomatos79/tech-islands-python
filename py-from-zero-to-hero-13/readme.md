# Challenge Overview: Build a Custom VS Code Extension Using Ollama + qwen2.5-coder
This challenge explores how to integrate local LLM capabilities directly into the development workflow by building a custom VS Code extension that communicates with a Python API powered by Ollama and the `qwen2.5-coder` model. The goal is to improve code editing productivity without relying on cloud-based LLM services.

## Objectives
The challenge consists of three core objectives:

### 1) VS Code Extension Development (TypeScript)
Create a custom extension using the VS Code Extension SDK to:
- interact with user code selections
- trigger context menu commands
- communicate with an external API
- write new files dynamically (for example, generated test files)
- update the current document programmatically

### 2) Local LLM Execution with Ollama
Use Ollama locally to avoid network dependency and allow full customization:
- load and run the `qwen2.5-coder` model
- handle developer tasks such as:
  - fixing compilation/runtime errors
  - adding header documentation comments
  - generating test files

### 3) Custom Backend API (Python + Flask/FastAPI)
Implement a lightweight Python backend exposing a single `/analyze` endpoint that:
- receives code, language, and task instructions from the extension
- formats prompts for the model
- returns structured JSON responses

## Key Features Completed in This Challenge
During the build phase, the following features were implemented:
- Local execution using Ollama + `qwen2.5-coder`
- Custom `/analyze` API with structured tasks
- VS Code right-click context menu commands
- Code-driven transformations:
  - Fix Errors
  - Generate Unit Tests
  - Add Header Comments
- Test generation workflow that prompts for output file name
- Integration with VS Code file system APIs
- Progress notifications ("Processing request…")
- `.vsix` packaging for installation and distribution
- Versioned build pipeline using `npm run build`
- Optional Dockerization for the Python backend
- Ability to run fully offline

## Comparison Table (Claude and Claude-like Alternatives)
| Feature | Claude | Best local equivalents |
| --- | --- | --- |
| General reasoning | Opus | DeepSeek-R1 |
| Developer tasks | Sonnet | Qwen 2.5 Coder |
| Balanced chat | Sonnet | Llama-3.1 |
| Fast chat | Haiku | Mistral Nemo |
| Safety | Very high | Medium |
| Context window | Very large | Small–medium |

## Project Structure
```bash
py-from-zero-to-hero-13/
  src/
    api/
      main.py
      requirements.txt
    vscode-extension/
      LICENSE.md
      package.json
      tsconfig.json
      src/
        extension.ts
```

## First: Run the API

### Run Docker Ollama (port 11435)
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

### Pull the `qwen2.5-coder` model
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

### Check the model list
```bash
ollama list
```

Expected output includes `qwen2.5-coder` (example):
```bash
NAME                    ID              SIZE      MODIFIED
qwen2.5-coder:latest    dae161e27b0e    4.7 GB    About a minute ago
```

### Confirm Ollama is ready
```bash
curl http://localhost:11435/api/tags
```

Example output:
```json
{"models":[{"name":"llava:latest","model":"llava:latest","modified_at":"2026-01-27T15:59:45.933695009Z","size":4733363377,"digest":"8dd30f6b0cb19f555f2c7a7ebda861449ea2cc76bf1f44e262931f45fc81d081","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama","clip"],"parameter_size":"7B","quantization_level":"Q4_0"}},{"name":"llama3.2:latest","model":"llama3.2:latest","modified_at":"2026-01-20T14:57:16.960827012Z","size":2019393189,"digest":"a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama"],"parameter_size":"3.2B","quantization_level":"Q4_K_M"}}]}
```

### Set environment variables
```bash
export OLLAMA_URL=http://localhost:11435
export OLLAMA_MODEL=qwen2.5-coder
```

### Run the API
```bash
cd py-from-zero-to-hero-13
python3.11 -m venv vscodext
source vscodext/bin/activate
pip install -r ./src/api/requirements.txt
cd ./src/api
```

Lets run the API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Line-by-line meaning:
- uvicorn → runs the FastAPI app (ASGI server)
- main:app → load app object from main.py
- --reload → auto-restart the server when we change code (dev only)
- --host 0.0.0.0 → make the server accessible from outside the machine (not just localhost)
- --port 8000 → expose the server on port 8000

Expected output:
```bash
INFO:     Will watch for changes in these directories: ['/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-13/src/api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [59364] using WatchFiles
INFO:     Started server process [59366]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Verify the API
```bash
curl http://localhost:8000/ping
```

Expected output:
```json
{"status":"ok"}
```

### Validate the LLM
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "fix_errors",
    "language": "python",
    "code": "pint(x)"
  }'
```

Expected output:
```json
{"updated_code":"```python\nprint(x)\n```","notes":"Task 'fix_errors' applied by LLM."}
```

## Building the VS Code Extension

### Install Node.js
```bash
brew install node
```

### Confirm versions
```bash
node -v
# v25.5.0

npm -v
# 11.8.0
```

### Install project dependencies
```bash
cd py-from-zero-to-hero-13/src/vscode-extension
npm install
```

### Compile and build the extension
```bash
cd py-from-zero-to-hero-13/src/vscode-extension
npm run build
```

Expected output:
```bash
> python-adventure@0.0.8 build
> npm run compile && vsce package

> python-adventure@0.0.8 compile
> tsc -p ./

(node:73026) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
Executing prepublish script 'npm run vscode:prepublish'...
(node:73026) [DEP0190] DeprecationWarning: Passing args to a child process with shell option true can lead to security vulnerabilities, as the arguments are not escaped, only concatenated.

> python-adventure@0.0.8 vscode:prepublish
> npm run compile

> python-adventure@0.0.8 compile
> tsc -p ./

This extension consists of 523 files, out of which 150 are JavaScript files. For performance reasons, you should bundle your extension: https://aka.ms/vscode-bundle-extension . You should also exclude unnecessary files by adding them to your .vscodeignore: https://aka.ms/vscode-vscodeignore
DONE  Packaged: /Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-13/src/vscode-extension/python-adventure-0.0.8.vsix (523 files, 2.33MB)
```

The generated `.vsix` file is located at:
```bash
/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-13/src/vscode-extension/python-adventure-0.0.8.vsix
```

## Install and Test the Extension

### Install the extension
1. Open the Extensions panel in VS Code.
2. Click the "..." menu and choose "Install from VSIX...".
3. From the `vscode-extension` folder, select the `.vsix` file and click the blue Install button.

![Extensions panel](./imgs/image.png)
![Install VSIX](./imgs/image-1.png)
![Select VSIX file](./imgs/image-2.png)

### Fix Errors workflow
1. In the `demo` folder, open `main.py`.
2. Select the invalid function block:

```python
def calc(a, b):
    return := a * b
```

3. Right-click and choose **Python Adventure: Fix Errors**.

![Fix Errors menu](./imgs/image-4.png)

A progress notification appears at the bottom-right:

![Progress notification](./imgs/image-5.png)

### Verify request in the API terminal
```bash
(vscodext) renatomatos@PT-D144L6PXF0 api % uvicorn main:app --reload --host 0.0.0.0 --port 8000
INFO:     Will watch for changes in these directories: ['/Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-13/src/api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [74063] using WatchFiles
INFO:     Started server process [74065]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

API response:
```bash
[OLLAMA] URL: http://localhost:11435, model: qwen2.5-coder
[OLLAMA] Status: 200
[OLLAMA] Body: {"model":"qwen2.5-coder","created_at":"2026-01-28T15:41:56.376718502Z","message":{"role":"assistant","content":"```python\ndef calc(a, b):\n    return a * b\n```"},"done":true,"done_reason":"stop","total_duration":1745098209,"load_duration":106029792,"prompt_eval_count":101,"prompt_eval_duration":512736875,"eval_count":17,"eval_duration":1109351749}
INFO:     127.0.0.1:59211 - "POST /analyze HTTP/1.1" 200 OK
```

### Expected code fix
Before:
```python
def calc(a, b):
    return := a * b
```

After:
```python
def calc(a, b):
    return a * b
```

### Generate unit tests
1. Select the function body:

```python
def calc(a, b):
    return a * b
```

2. Right-click and choose **Python Adventure: Generate Unit Tests**.

![Generate tests menu](./imgs/image-6.png)

3. Accept the suggested output file name from the dropdown.

![Test file suggestion](./imgs/image-7.png)

4. Open `test_main.py` and fix the import to include `calc`.

Original test file content:
```python
import unittest

class TestCalc(unittest.TestCase):

    def test_calc_with_positive_numbers(self):
        self.assertEqual(calc(2, 3), 6)

    def test_calc_with_negative_numbers(self):
        self.assertEqual(calc(-2, 3), -6)

    def test_calc_with_zero(self):
        self.assertEqual(calc(0, 5), 0)

if __name__ == '__main__':
    unittest.main()
```

Fixed import:
```python
import unittest
from main import calc
```

5. Run tests using **Python Adventure: Run Tests**.

![Run tests](./imgs/image-8.png)

We should see the terminal output window:

![Test output](./imgs/image-9.png)


# Let's build another topic: breaking down the VS Code extension
Inside the `vscode-extension` folder we have the core files. Let's start with `package.json`.
```json
{
  "name": "python-adventure",
  "displayName": "Python Adventure Smart Code Assistant",
  "description": "Generate tests, add header comments and fix errors using our own LLM API.",
  "version": "0.0.9",
  "publisher": "Renato Matos",
  "engines": {
    "vscode": "^1.84.0"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/renatomatos79/python-adventure.git"
  },
  "license": "MIT",
  "icon": "icon.png",
  "galleryBanner": {
    "color": "#1e1e1e",
    "theme": "dark"
  },
  "main": "./out/extension.js",
```

These initial fields describe the extension and include:\n+- extension name and display name\n+- version used to build the `.vsix` file\n+- publisher\n+- supported VS Code engine version\n+- source repository\n+- license\n+- extension icon and basic theme settings

## activationEvents section
These define when the extension is activated.
```json
"activationEvents": [
    "onCommand:python-adventure.setApiEndpoint",
    "onCommand:python-adventure.generateTests",
    "onCommand:python-adventure.addHeaderComments",
    "onCommand:python-adventure.fixErrors"
],
```

`onCommand:<command-id>`\n+- Activate the extension when that command is executed.\n+- Command IDs must match the `commands` section in `package.json`.\n+\n+What each event means:

`onCommand:python-adventure.setApiEndpoint` activates when the user runs `python-adventure.setApiEndpoint`.

`onCommand:python-adventure.generateTests` activates when test generation is triggered.

`onCommand:python-adventure.addHeaderComments` activates when the user asks to add header comments.

`onCommand:python-adventure.fixErrors` activates when the user requests error fixing.

**Commands can be triggered by:**

- Command Palette (Ctrl+Shift+P)
- Keyboard shortcuts
- Context menus
- API calls from other extensions

**Important:**

For each command there is a corresponding task implemented in `src/extension.ts`. Each command ID maps to an internal handler that runs the appropriate logic.

## contributes section
The `contributes` section tells VS Code which features the extension adds. Examples include:

- commands
- menus
- keybindings
- languages
- themes
- snippets

In this project, we contribute commands and menu entries.
```json

"commands": [
  {
    "command": "python-adventure.generateTests",
    "title": "Python Adventure: Generate Unit Tests"
  },
  ...
]
```

Each item defines a command with two fields:

`title`: Human-friendly label shown in the UI (Command Palette, etc.).

`command`: Internal ID used in code. This must match what our extension listens for.

For example, in TypeScript we register the command like this:

```ts
vscode.commands.registerCommand("python-adventure.generateTests", handler);
```

## menus section


```json
"menus": {
  "editor/context": [
    {
      "command": "python-adventure.generateTests",
      "group": "python-adventure",
      "when": "editorHasSelection"
    },
    ...
  ]
}
```

This defines where commands appear in the VS Code UI. Here, `editor/context` means:

Right-click context menu inside the editor.

**Breaking down one menu entry:**

`command`: Which command to show in that menu.

`group`: Controls ordering and grouping in the menu. Optional but helps organize layout.

`when`: Determines when it should be visible. 

`editorHasSelection` means only show if the user has selected text.

So the UX becomes:
User selects some code, right-clicks, and sees **Generate Tests** + **Fix Errors**.

User with no selection only sees **Run Tests**.

## scripts section

```json
 "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "vscode:prepublish": "npm run compile",
    "build": "npm run compile && vsce package"
  },
```

- `compile`: Runs TypeScript using `tsconfig.json` and converts `.ts` to `.js`.
- `watch`: Same as compile, but watches for file changes and recompiles automatically while editing.
- `vscode:prepublish`: VS Code uses this hook before publishing or packaging. It compiles everything first.
- `build`: Runs `npm run compile` and then `vsce package`.

## tsconfig.json file
`tsconfig.json` tells the TypeScript compiler how to convert TypeScript (`.ts`) into JavaScript (`.js`).\n+Think of it as:\n+> “Here is how I want TypeScript to behave in this project.”
\n+For this extension we configure the compiler as follows:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "out",
    "rootDir": "src",
    "strict": true,
    "sourceMap": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}

```

### compilerOptions
These settings affect how TypeScript compiles code.

- `target: "ES2020"`  
When generating JavaScript, use ES2020 features (async/await, classes, etc.).

- `module: "commonjs"`
Defines the module system for imports/exports. CommonJS is what Node.js uses:

```ts
module.exports = ...
const x = require('...')
```

- `lib: ["ES2020"]`
Tells TypeScript which built-in APIs exist in our environment (Promise, Map, Set, etc.).

- `outDir: "out"`
Generated `.js` files go into the `out/` folder.

- `rootDir: "src"`
Our `.ts` source files live in `src/`.

- `strict: true`
Enables all strict type checks, which helps catch bugs early (undefined variables, wrong types, missing returns).

- `sourceMap: true`
Generates `.map` files so we can debug TypeScript inside VS Code while running JavaScript.

- `esModuleInterop: true`
Lets us mix module styles:
```javascript
import fs from "fs"
```

instead of:
```javascript
import * as fs from "fs"
```

- skipLibCheck: true
Skips type checking inside libraries we install via npm.
Builds become faster, errors become less noisy.

- forceConsistentCasingInFileNames: true
Prevents bugs where file paths differ by upper/lowercase — especially useful on Windows vs Linux.
Example bug without it:

```javascript
import "./Utils"
import "./utils"
```

As a result, Linux would break, Windows wouldn’t.

include:
```json
"include": ["src"]
```

“Only compile .ts files inside the src folder.”

If you wish to learn more about TypeScript I have this amazing Udemy training
https://www.udemy.com/course/microfrontend-na-pratica/