# OpenCode Integration: Google OmniMemory

Connect the **OpenCode** agent framework or CLI to **Google OmniMemory** for zero-token-bloat execution.

---

## 🚀 Setup

OpenCode supports standard Model Context Protocol (MCP) integrations. Point OpenCode's configuration to the OmniMemory stdio MCP server:

```json
{
  "mcpServers": {
    "google-omnimemory": {
      "command": "python",
      "args": ["-m", "omni_memory.mcp"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

---

## ⚡ Available Tools in OpenCode

- **`omnimemory_track_step`**: Stores execution deliberations and intermediate code AST transformations out-of-band in Google LevelDB WAL.
- **`omnimemory_query_scann`**: Fast sub-linear vector search over past memories.
- **`omnimemory_trigger_callback`**: Triggers a callback event with `source="opencode"`, causing the Glassmorphism webapp (`http://127.0.0.1:8765/`) to display an electric cobalt `[OPENCODE]` toast and synchronize the related template.
