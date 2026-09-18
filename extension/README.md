# Google OmniMemory - VS Code Plugin Tool

The official VS Code extension for **Google OmniMemory**, the open-source Decoupled Memory Agent & Allocator fusing Google open-source technologies:
- **Always-On Memory Agent** (Background distillation)
- **Google Research ReasoningBank** (Episodic milestones & reasoning templates)
- **Google Diff-Match-Patch** (Semantic context diffs via Myers algorithm)
- **Google LevelDB** (Out-of-band write-ahead log ledger)
- **Google ScaNN** (High-dimensional vector search)
- **Google SentencePiece** (Sub-word token budget enforcement)

---

## Features

- ⚡ **Interactive Real-Time Dashboard**: Native VS Code Webview panel displaying token savings KPIs, live step stream, canonical revised context, and active prompt inspector.
- 🎯 **Callback Integration with Related Templates**: Trigger callbacks from VS Code or CLI that instantly synchronize the dashboard and highlight the related ReasoningBank task template (`raft`, `trading`, `refactor`, `research`).
- 🔍 **Google ScaNN Vector Memory Search**: Search your agent's long-term memory directly from the VS Code command palette without bloating the LLM prompt.
- 🛠️ **Automated Server Lifecycle**: Automatically spawns and manages the local Python dashboard server using Miniconda Python.
- 📊 **Status Bar Token Economics**: Live indicator showing prompt tokens shielded and saved.

---

## Commands

| Command | Title | Description |
|---|---|---|
| `omniMemory.openDashboard` | **OmniMemory: Open Real-Time Dashboard** | Opens the Glassmorphism console inside a VS Code webview or external browser. |
| `omniMemory.triggerCallback` | **OmniMemory: Trigger Callback & Show Template** | QuickPick for templates (`raft`, `trading`, etc.), executes callback, and focuses dashboard & template. |
| `omniMemory.selectTemplate` | **OmniMemory: Select Reasoning Template** | Switches the active prompt template and bounded token budget. |
| `omniMemory.queryScann` | **OmniMemory: Query ScaNN Vector Memory** | Prompts for query and returns nearest neighbor memory slots with cosine similarity. |
| `omniMemory.runSimulation` | **OmniMemory: Run Multi-Step Reasoning Simulation** | Triggers an automated 6-step reasoning trajectory with real-time SSE updates. |
| `omniMemory.startServer` | **OmniMemory: Start Dashboard Server** | Manually spawns the dashboard server on the configured port. |

---

## Configuration Settings

Under VS Code Settings (`Ctrl+,` or `Cmd+,`), search for **OmniMemory**:

- `omniMemory.serverPort`: Default `8765`. Port for the dashboard and API.
- `omniMemory.pythonPath`: Path to your Python interpreter (default: `python`).
- `omniMemory.autoStartServer`: Default `true`. Auto-starts the dashboard server when commands are executed.

---

## Installation into VS Code

To install locally as a developer extension:
1. Open this folder in VS Code.
2. Symlink or copy the `extension` folder into your VS Code extensions directory:
   - Windows: `%USERPROFILE%\.vscode\extensions\google-omnimemory`
   - Linux/macOS: `~/.vscode/extensions/google-omnimemory`
3. Reload VS Code (`Developer: Reload Window`).
