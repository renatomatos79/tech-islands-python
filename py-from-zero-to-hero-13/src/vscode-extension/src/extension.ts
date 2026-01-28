import * as vscode from 'vscode';
import fetch from 'node-fetch';

const API_ENDPOINT_KEY = 'free-forever';

type TaskType = 'generate_tests' | 'add_header_comments' | 'fix_errors';

export function activate(context: vscode.ExtensionContext) {
  console.log("Python Adventure extension activated");

  
  const setEndpointCmd = vscode.commands.registerCommand(
    'python-adventure.setApiEndpoint',
    () => setApiEndpoint(context)
  );

  const generateTestsCmd = vscode.commands.registerCommand(
    'python-adventure.generateTests',
    () => runTaskOnSelection(context, 'generate_tests')
  );

  const addHeaderCommentsCmd = vscode.commands.registerCommand(
    'python-adventure.addHeaderComments',
    () => runTaskOnSelection(context, 'add_header_comments')
  );

  const fixErrorsCmd = vscode.commands.registerCommand(
    'python-adventure.fixErrors',
    () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;

      const selection = editor.selection;
      const text = editor.document.getText(selection);

      if (!text) {
        vscode.window.showInformationMessage('Select code first');
        return;
      }

      runTaskOnSelection(context, 'fix_errors')
    }
  );


  context.subscriptions.push(
    setEndpointCmd,
    generateTestsCmd,
    addHeaderCommentsCmd,
    fixErrorsCmd
  );
}

export function deactivate() {
  // nothing special
  console.log("why? :(")
}

async function setApiEndpoint(context: vscode.ExtensionContext) {
  const current = context.globalState.get<string>(API_ENDPOINT_KEY);

  const url = await vscode.window.showInputBox({
    title: 'Smart Code Assistant API URL',
    prompt: 'Enter the base URL of your Python API (e.g. http://localhost:8000)',
    value: current ?? 'http://localhost:8000',
    ignoreFocusOut: true,
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
      `Smart Code Assistant endpoint set to ${normalized}`
    );
  } catch (err: any) {
    vscode.window.showErrorMessage(
      `Failed to ping API at ${normalized}: ${err?.message ?? String(err)}`
    );
  }
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
      'API endpoint not set. Configure it first.',
      'Set API Endpoint'
    );
    if (choice === 'Set API Endpoint') {
      await setApiEndpoint(context);
    }
    return;
  }

  const document = editor.document;
  const selection = editor.selection;

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

  const loading = vscode.window.setStatusBarMessage(
    `Smart Code Assistant: running task '${task}'...`
  );

  try {
    const res = await fetch(`${apiBase}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        task,
        language: languageId,
        code,
      }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }

    const body = (await res.json()) as {
      updated_code: string;
      notes?: string;
    };

    await editor.edit((editBuilder) => {
      editBuilder.replace(range, body.updated_code);
    });

    if (body.notes) {
      vscode.window.showInformationMessage(body.notes);
    } else {
      vscode.window.showInformationMessage(
        `Smart Code Assistant: '${task}' completed.`
      );
    }
  } catch (err: any) {
    vscode.window.showErrorMessage(
      `Smart Code Assistant error: ${err?.message ?? String(err)}`
    );
  } finally {
    loading.dispose();
  }
}
