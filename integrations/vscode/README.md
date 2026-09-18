# Visual Studio Code Integration Guide for G-OmniOS

Use **G-OmniOS** directly within Visual Studio Code through three powerful methods:
1. **Native VS Code Extension**: Status bar token counter, command palette, and embedded Glassmorphism webview.
2. **VS Code MCP (Cline, Roo Code, Claude Dev, Continue)**: Model Context Protocol agent tool integration.
3. **Task & Terminal Automation**: One-click scripts and background daemons.

---

## 💻 1. Native VS Code Extension

The extension is located in the `extension/` directory.

### Quick Install / Test:
1. In VS Code, open the repository root directory.
2. Press `F5` (or run **Debug: Start Debugging**) with the VS Code Extension Host.
3. A new VS Code Development Host window will launch with G-OmniOS loaded!

### Features:
- **Status Bar Item**: Real-time counter showing `$(database) G-OmniOS: X tok saved`. Clicking it opens the webview dashboard.
- **Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)**:
  - `G-OmniOS: Open Live Dashboard Panel`
  - `G-OmniOS: Query Semantic Memory (ScaNN)`
  - `G-OmniOS: Run Mind4Action Cognitive Cycle`
  - `G-OmniOS: Inspect & Optimize Prompt Context`
  - `G-OmniOS: Start Local Dashboard Server`

---

## 🤖 2. MCP Setup for Cline, Roo Code, and Claude Dev

If you use AI coding agents inside VS Code such as **Cline**, **Roo Code**, **Claude Dev**, or **Continue**:

1. Open your agent's MCP settings:
   - For Cline: Click the MCP icon in the top header -> **Edit MCP Settings**.
   - Or open `.vscode/settings.json` or `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`.
2. Add the `g-omnios` MCP server:

```json
{
  "mcpServers": {
    "g-omnios": {
      "command": "python",
      "args": ["-m", "omni_memory.mcp"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

Now Cline / Roo Code / Claude Dev can autonomously:
- Log intermediate reasoning steps out-of-band to save 70%–90% prompt tokens.
- Perform ScaNN vector lookups of past architectural decisions.
- Execute structured Mind4Action cycles (`Perceive -> Reflect -> Intend -> Act`).
- Consult organizational agent teams (Manager, HR, Fullstack, DevOps).

---

## ⚙️ 3. Settings Configuration

Add the following to `.vscode/settings.json` for customized behavior:

```json
{
  "gomnios.serverUrl": "http://127.0.0.1:8765",
  "gomnios.autoStartServer": true,
  "gomnios.showStatusBar": true
}
```
