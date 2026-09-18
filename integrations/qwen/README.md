# Qwen Integration Guide for G-OmniOS

Connect **Qwen** (Qwen Desktop, Qwen 2.5 / Qwen 2.5-Coder models, Qwen-Agent framework, Ollama, LM Studio, or Open-WebUI) directly to **G-OmniOS**.

---

## 🚀 1. Qwen Desktop App (MCP Setup)

If using Qwen Desktop with Model Context Protocol (MCP) support:

1. Open Qwen Desktop settings or config directory.
2. Add the following entry to your `mcp_servers.json` or `config.json`:

```json
{
  "mcpServers": {
    "g-omnios": {
      "command": "python",
      "args": ["-m", "omni_memory.mcp"],
      "env": {
        "PYTHONPATH": "<PATH_TO_G_OMNIOS_ROOT>"
      }
    }
  }
}
```

3. Restart Qwen Desktop. Qwen now has direct access to:
   - `gomnios_mind4action_cycle`: 4-phase reasoning (`Perceive -> Reflect -> Intend -> Act`).
   - `omnimemory_track_step`: Zero-token out-of-band persistent memory logging to LevelDB WAL.
   - `omnimemory_query_scann`: Sub-millisecond vector semantic retrieval.
   - `gomnios_schedule_persona_skill`: Technical, Social, and Mental skill scheduling.
   - `gomnios_department_dispatch`: Specialized agent delegation (Manager, HR, Fullstack, Marketing, DevOps).

---

## 🐍 2. Qwen-Agent Python Framework Integration

Use the provided adapter `qwen_agent_tools.py`:

```python
from qwen_agent.agents import Assistant
from omni_memory.engine import GOmniOSSystem

# Initialize G-OmniOS
gomnios = GOmniOSSystem()

# Run Mind4Action reasoning loop
result = gomnios.mind4action_cycle("Design a high-throughput microservices architecture with Raft consensus")

print("Reflection CLI:", result["reflection"]["cli"])
print("Flow Score:", result["reflection"]["flow_score"])
print("Intended Action:", result["intention"]["target_action"])
```

---

## 🦙 3. Ollama & Local Qwen Models (Qwen 2.5 / Coder)

When running Qwen locally via Ollama or LM Studio, connect via the G-OmniOS REST API:

- Start G-OmniOS server:
  ```bash
  g-omnios serve --port 8765
  ```
- Send requests from your local Qwen agent loop:
  - `POST http://127.0.0.1:8765/api/mind4action`
  - `POST http://127.0.0.1:8765/api/step`
  - `POST http://127.0.0.1:8765/api/query`
  - `GET  http://127.0.0.1:8765/api/telemetry`
