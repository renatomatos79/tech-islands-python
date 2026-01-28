import * as vscode from 'vscode';

const API_ENDPOINT_KEY = 'python-adventure.apiEndpoint';

type TaskType = 'generate_tests' | 'add_header_comments' | 'fix_errors';

export function activate(context: vscode.ExtensionContext) {
  console.log('Python Adventure extension activated');

  const setEndpointCmd = vscode.commands.registerCommand(
    'python-adventure.setApiEndpoint',
    async () => {
      await setApiEndpoint(context);
    }
  );

  const generateTestsCmd = vscode.commands.registerCommand(
    'python-adventure.generateTests',
    async () => {
      await runTaskOnSelection(context, 'generate_tests');
    }
  );

  const addHeaderCommentsCmd = vscode.commands.registerCommand(
    'python-adventure.addHeaderComments',
    async () => {
      await runTaskOnSelection(context, 'add_header_comments');
    }
  );

  const fixErrorsCmd = vscode.commands.registerCommand(
    'python-adventure.fixErrors',
    async () => {
      await runTaskOnSelection(context, 'fix_errors');
    }
  );

  const runTestsCmd = vscode.commands.registerCommand(
    'python-adventure.runTests',
    async () => {
      const task = new vscode.Task(
        { type: 'python-adventure' },
        vscode.TaskScope.Workspace,
        'Run Python Tests',
        'python-adventure',
        new vscode.ShellExecution('pytest -q')
      );
      vscode.tasks.executeTask(task);
    }
  );

  context.subscriptions.push(
    setEndpointCmd,
    generateTestsCmd,
    addHeaderCommentsCmd,
    fixErrorsCmd,
    runTestsCmd
  );
}




export function deactivate() {
  console.log('Python Adventure extension deactivated');
}

function stripCodeFences(text: string): string {
  return text.replace(/```[\s\S]*?```/g, match => {
    return match.replace(/```[\w]*/g, "").replace(/```/g, "").trim();
  });
}

async function setApiEndpoint(context: vscode.ExtensionContext) {
  const current = context.globalState.get<string>(API_ENDPOINT_KEY);

  const url = await vscode.window.showInputBox({
    title: 'Python Adventure API URL',
    prompt:
      'Enter the base URL of your Python Adventure API (e.g. http://localhost:8000)',
    value: current ?? 'http://localhost:8000',
    ignoreFocusOut: true
  });

  if (!url) {
    return;
  }

  const normalized = url.replace(/\/+$/, '');

  try {
    const res = await fetch(`${normalized}/ping`);
    if (!res.ok) {
      throw new Error(`Status ${res.status}`);
    }
    const json = (await res.json()) as { status?: string };
    if (json.status !== 'ok') {
      throw new Error(`Unexpected ping response: ${JSON.stringify(json)}`);
    }

    await context.globalState.update(API_ENDPOINT_KEY, normalized);
    vscode.window.showInformationMessage(
      `Python Adventure API endpoint set to ${normalized}`
    );
  } catch (err: any) {
    vscode.window.showErrorMessage(
      `Failed to ping API at ${normalized}: ${err?.message ?? String(err)}`
    );
  }
}

async function handleGenerateTestsResult(
  document: vscode.TextDocument,
  languageId: string,
  testCode: string
) {
  // Suggest a default test file name based on the current file
  const originalFileName = document.fileName.split(/[\\/]/).pop() || 'code.py';

  let defaultTestName = originalFileName;
  if (originalFileName.endsWith('.py')) {
    defaultTestName = `test_${originalFileName}`;
  } else {
    defaultTestName = `${originalFileName}.test`;
  }

  const testFileName = await vscode.window.showInputBox({
    title: 'Python Adventure: Test file name',
    prompt: 'Enter the filename to save the generated tests',
    value: defaultTestName,
    ignoreFocusOut: true
  });

  if (!testFileName) {
    vscode.window.showWarningMessage(
      'Python Adventure: tests not created (no file name provided).'
    );
    return;
  }

  const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);

  if (!workspaceFolder) {
    // No workspace open: just open an untitled document with the test code
    const testDoc = await vscode.workspace.openTextDocument({
      content: testCode,
      language: languageId
    });
    await vscode.window.showTextDocument(testDoc);
    return;
  }

  // Create the file in the workspace root (you could later make this configurable)
  const testFileUri = vscode.Uri.joinPath(workspaceFolder.uri, testFileName);

  // Write file contents
  const encoder = new TextEncoder();
  const bytes = encoder.encode(testCode);
  await vscode.workspace.fs.writeFile(testFileUri, bytes);

  const testDoc = await vscode.workspace.openTextDocument(testFileUri);
  await vscode.window.showTextDocument(testDoc);

  vscode.window.showInformationMessage(
    `Python Adventure: tests written to ${testFileName}`
  );
}


async function runTaskOnSelection(
  context: vscode.ExtensionContext,
  task: TaskType
) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('No active editor.');
    return;
  }

  const apiBase = context.globalState.get<string>(API_ENDPOINT_KEY);
  if (!apiBase) {
    const choice = await vscode.window.showWarningMessage(
      'Python Adventure API endpoint not set.',
      'Set API Endpoint'
    );
    if (choice === 'Set API Endpoint') {
      await setApiEndpoint(context);
    }
    return;
  }

  const document = editor.document;
  const selection = editor.selection;

  // If no selection, operate on the whole file
  const range = selection.isEmpty
    ? new vscode.Range(
      0,
      0,
      document.lineCount - 1,
      document.lineAt(document.lineCount - 1).text.length
    )
    : selection;

  const code = document.getText(range);

  if (!code.trim()) {
    vscode.window.showWarningMessage('Nothing to send: selection is empty.');
    return;
  }

  const languageId = document.languageId; // "python", "typescript", etc.

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: `Python Adventure: processing request...`,
      cancellable: false
    },
    async () => {
      try {
        const res = await fetch(`${apiBase}/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task,
            language: languageId,
            code
          })
        });

        if (!res.ok) {
          const text = await res.text();
          throw new Error(`HTTP ${res.status}: ${text}`);
        }

        const body = (await res.json()) as {
          updated_code: string;
          notes?: string;
        };

        if (task === 'generate_tests') {
          await handleGenerateTestsResult(document, languageId, stripCodeFences(body.updated_code));
        } else {
          // For add_header_comments and fix_errors: replace code in place
          await editor.edit((editBuilder) => {
            editBuilder.replace(range, stripCodeFences(body.updated_code));
          });
        }

        if (body.notes) {
          vscode.window.showInformationMessage(body.notes);
        } else {
          vscode.window.showInformationMessage(
            `Python Adventure: '${task}' completed.`
          );
        }
      } catch (err: any) {
        vscode.window.showErrorMessage(
          `Python Adventure error: ${err?.message ?? String(err)}`
        );
      }
    }
  );
}

