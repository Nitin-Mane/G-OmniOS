/**
 * Google OmniMemory - VS Code Plugin Tool
 * 
 * Provides native VS Code integration for the decoupled Google OmniMemory Agent & Allocator:
 * - Real-time Webview Dashboard embedding the Glassmorphism console
 * - Callback execution with template selection and synchronization
 * - Out-of-band step tracking and ScaNN semantic query execution
 * - Automated background server lifecycle management via Miniconda Python
 */

const vscode = require("vscode");
const http = require("http");
const { spawn } = require("child_process");
const path = require("path");

let currentPanel = null;
let serverProcess = null;
let statusBarItem = null;

const TEMPLATE_OPTIONS = [
  {
    id: "raft",
    label: "$(server-process) Raft Consensus & Distributed State Machine",
    description: "Distributed Systems • 600 tokens budget",
    detail: "Leader election, heartbeat replication, quorum safety, and log compaction with strict out-of-band step tracking.",
    sampleQuery: "network partition minority leader"
  },
  {
    id: "trading",
    label: "$(graph-line) Algorithmic Trading & Risk Parity Strategy",
    description: "Quantitative Finance • 800 tokens budget",
    detail: "Covariance matrix deconstruction, volatility budgeting, dynamic leverage scaling, and ScaNN rule indexing.",
    sampleQuery: "volatility targeting rule"
  },
  {
    id: "refactor",
    label: "$(symbol-structure) Autonomous Code Refactoring & Invariant Synthesis",
    description: "Software Engineering • 700 tokens budget",
    detail: "Zero-regression codebase modernization, invariant extraction, AST transformation, and Diff-Match-Patch delta auditing.",
    sampleQuery: "diff match patch myers delta"
  },
  {
    id: "research",
    label: "$(book) Multi-Step Scientific & Literature Synthesis",
    description: "Research & Analysis • 900 tokens budget",
    detail: "High-throughput paper abstraction, cross-source fact distillation, hypothesis generation, and ReasoningBank milestone logging.",
    sampleQuery: "lost in the middle context degradation"
  }
];

function activate(context) {
  // Status Bar Item
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = "omniMemory.openDashboard";
  statusBarItem.text = "$(chip) OmniMemory";
  statusBarItem.tooltip = "Google OmniMemory: Decoupled Agent Memory Allocator (Click to open dashboard)";
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);

  // Command: Open Dashboard Webview
  const cmdOpenDashboard = vscode.commands.registerCommand("omniMemory.openDashboard", async (templateId) => {
    const config = vscode.workspace.getConfiguration("omniMemory");
    const port = config.get("serverPort") || 8765;
    const autoStart = config.get("autoStartServer") !== false;

    const isRunning = await isServerRunning(port);
    if (!isRunning && autoStart) {
      await startServer(context, port);
    }

    createOrShowWebview(context, port, templateId || "raft");
  });

  // Command: Trigger Callback
  const cmdTriggerCallback = vscode.commands.registerCommand("omniMemory.triggerCallback", async () => {
    const config = vscode.workspace.getConfiguration("omniMemory");
    const port = config.get("serverPort") || 8765;
    const autoStart = config.get("autoStartServer") !== false;

    // 1. Prompt user to select template
    const selected = await vscode.window.showQuickPick(TEMPLATE_OPTIONS, {
      placeHolder: "Select ReasoningBank template to activate with callback",
      matchOnDescription: true,
      matchOnDetail: true
    });

    if (!selected) return;

    // 2. Prompt for optional task note / callback message
    const msg = await vscode.window.showInputBox({
      prompt: `Enter callback reasoning note or step context for [${selected.id}]`,
      placeHolder: `e.g., Initiating ${selected.id} reasoning iteration from VS Code`,
      value: `VS Code Trigger: Active reasoning task on ${selected.id}`
    });

    if (msg === undefined) return; // User cancelled

    // 3. Ensure server is running
    const isRunning = await isServerRunning(port);
    if (!isRunning && autoStart) {
      vscode.window.showInformationMessage(`Starting OmniMemory Server on port ${port}...`);
      await startServer(context, port);
      await new Promise(r => setTimeout(r, 1200));
    }

    // 4. Send POST /api/callback
    const payload = {
      event: "VS Code Callback Event",
      template_id: selected.id,
      source: "vscode",
      payload: {
        message: msg,
        timestamp: Date.now() / 1000
      }
    };

    try {
      const resp = await postJson(`http://127.0.0.1:${port}/api/callback`, payload);
      vscode.window.showInformationMessage(
        `OmniMemory: Callback triggered for template "${selected.id}". Synchronizing dashboard...`,
        "Open in Browser"
      ).then(choice => {
        if (choice === "Open in Browser") {
          vscode.env.openExternal(vscode.Uri.parse(`http://127.0.0.1:${port}/?template=${selected.id}&source=vscode`));
        }
      });

      // 5. Reveal / Update Webview with selected template
      createOrShowWebview(context, port, selected.id);

      if (currentPanel) {
        currentPanel.webview.postMessage({
          command: "selectTemplate",
          templateId: selected.id
        });
      }
    } catch (err) {
      vscode.window.showErrorMessage(`Failed to trigger OmniMemory callback: ${err.message}`);
    }
  });

  // Command: Select Template directly
  const cmdSelectTemplate = vscode.commands.registerCommand("omniMemory.selectTemplate", async () => {
    const selected = await vscode.window.showQuickPick(TEMPLATE_OPTIONS, {
      placeHolder: "Choose template to view in OmniMemory"
    });
    if (selected) {
      vscode.commands.executeCommand("omniMemory.openDashboard", selected.id);
    }
  });

  // Command: Query ScaNN Vector Memory
  const cmdQueryScann = vscode.commands.registerCommand("omniMemory.queryScann", async () => {
    const config = vscode.workspace.getConfiguration("omniMemory");
    const port = config.get("serverPort") || 8765;

    const query = await vscode.window.showInputBox({
      prompt: "Query Google ScaNN vector memory index",
      placeHolder: "e.g., 'network partition', 'volatility rule', 'diff match patch'"
    });

    if (!query) return;

    try {
      const resp = await postJson(`http://127.0.0.1:${port}/api/query`, { query, top_k: 5 });
      const results = resp.results || [];

      if (results.length === 0) {
        vscode.window.showInformationMessage(`No ScaNN vector matches found for "${query}".`);
        return;
      }

      const items = results.map(r => ({
        label: `$(search) [${Number(r.relevance).toFixed(3)}] ${r.tier.toUpperCase()} (${r.token_cost} tok)`,
        detail: r.content
      }));

      vscode.window.showQuickPick(items, {
        placeHolder: `ScaNN Results for "${query}"`
      });
    } catch (err) {
      vscode.window.showErrorMessage(`ScaNN search error: ${err.message}`);
    }
  });

  // Command: Run Simulation
  const cmdRunSimulation = vscode.commands.registerCommand("omniMemory.runSimulation", async () => {
    const config = vscode.workspace.getConfiguration("omniMemory");
    const port = config.get("serverPort") || 8765;

    try {
      await postJson(`http://127.0.0.1:${port}/api/simulate`, {});
      vscode.window.showInformationMessage("OmniMemory reasoning simulation started.");
      vscode.commands.executeCommand("omniMemory.openDashboard");
    } catch (err) {
      vscode.window.showErrorMessage(`Simulation trigger failed: ${err.message}`);
    }
  });

  // Command: Start Server
  const cmdStartServer = vscode.commands.registerCommand("omniMemory.startServer", async () => {
    const config = vscode.workspace.getConfiguration("omniMemory");
    const port = config.get("serverPort") || 8765;
    await startServer(context, port);
  });

  context.subscriptions.push(
    cmdOpenDashboard,
    cmdTriggerCallback,
    cmdSelectTemplate,
    cmdQueryScann,
    cmdRunSimulation,
    cmdStartServer
  );
}

function createOrShowWebview(context, port, templateId) {
  const column = vscode.window.activeTextEditor
    ? vscode.window.activeTextEditor.viewColumn
    : vscode.ViewColumn.One;

  if (currentPanel) {
    currentPanel.reveal(column);
    if (templateId) {
      currentPanel.webview.postMessage({ command: "selectTemplate", templateId });
    }
    return;
  }

  currentPanel = vscode.window.createWebviewPanel(
    "omniMemoryDashboard",
    "Google OmniMemory Console",
    column || vscode.ViewColumn.One,
    {
      enableScripts: true,
      retainContextWhenHidden: true
    }
  );

  currentPanel.webview.html = getWebviewContent(port, templateId);

  // Handle messages from the Webview
  currentPanel.webview.onDidReceiveMessage(
    (message) => {
      switch (message.type) {
        case "callbackReceived":
          vscode.window.showInformationMessage(`OmniMemory Webview synced: ${message.event} (${message.templateId})`);
          break;
        case "stateUpdate":
          if (statusBarItem && message.tokensSaved) {
            statusBarItem.text = `$(chip) Saved: ${message.tokensSaved} tok`;
          }
          break;
      }
    },
    undefined,
    context.subscriptions
  );

  currentPanel.onDidDispose(
    () => {
      currentPanel = null;
    },
    null,
    context.subscriptions
  );
}

function getWebviewContent(port, templateId) {
  const targetUrl = `http://127.0.0.1:${port}/?template=${templateId || "raft"}&source=vscode`;
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Google OmniMemory</title>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: #0b0f19;
    }
    iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
  </style>
</head>
<body>
  <iframe src="${targetUrl}" allow="clipboard-read; clipboard-write;"></iframe>
  <script>
    const vscode = acquireVsCodeApi();
    window.addEventListener("message", event => {
      const iframe = document.querySelector("iframe");
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage(event.data, "*");
      }
    });
  </script>
</body>
</html>`;
}

function isServerRunning(port) {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${port}/api/telemetry`, { timeout: 1000 }, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

function startServer(context, port) {
  return new Promise((resolve) => {
    const config = vscode.workspace.getConfiguration("omniMemory");
    const pythonPath = config.get("pythonPath") || "python";
    const workspaceRoot = path.resolve(__dirname, "..");

    if (serverProcess) {
      resolve(true);
      return;
    }

    serverProcess = spawn(pythonPath, ["-m", "omni_memory.cli", "serve", "--port", String(port)], {
      cwd: workspaceRoot,
      env: { ...process.env, PYTHONPATH: workspaceRoot }
    });

    serverProcess.stdout.on("data", (data) => {
      const str = data.toString();
      if (str.includes("Running on") || str.includes("Serving on")) {
        resolve(true);
      }
    });

    serverProcess.on("error", (err) => {
      vscode.window.showErrorMessage(`Failed to start OmniMemory server: ${err.message}`);
      serverProcess = null;
      resolve(false);
    });

    serverProcess.on("exit", () => {
      serverProcess = null;
    });

    setTimeout(() => resolve(true), 2000);
  });
}

function postJson(urlStr, data) {
  return new Promise((resolve, reject) => {
    const u = new URL(urlStr);
    const body = JSON.stringify(data);
    const req = http.request(
      {
        hostname: u.hostname,
        port: u.port,
        path: u.pathname + u.search,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(body)
        },
        timeout: 4000
      },
      (res) => {
        let respData = "";
        res.on("data", (c) => (respData += c));
        res.on("end", () => {
          try {
            resolve(JSON.parse(respData));
          } catch {
            resolve(respData);
          }
        });
      }
    );
    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("Request timed out"));
    });
    req.write(body);
    req.end();
  });
}

function deactivate() {
  if (serverProcess) {
    serverProcess.kill();
    serverProcess = null;
  }
}

module.exports = {
  activate,
  deactivate
};
