# Google Antigravity IDE Integration Guide for G-OmniOS

**Google Antigravity IDE** provides native, first-class support for **G-OmniOS** through workspace skills, project MCP servers, and background memory agents.

---

## 🌟 1. Workspace Skill Integration

G-OmniOS includes an Antigravity skill ready to use:
- Path: [`.agents/skills/omnimemory/SKILL.md`](../../.agents/skills/omnimemory/SKILL.md)

### When to Activate:
- Multi-step reasoning tasks, codebase refactoring, mathematical algorithms, and architecture design.
- Whenever you want the agent to save tokens by routing verbose scratchpad deliberations out-of-band to LevelDB WAL.
- Whenever you want sub-millisecond semantic search over previous conversation turns or codebase decisions using Google ScaNN.

---

## 🔌 2. Project MCP Server Configuration

G-OmniOS provides [`mcp_config.json`](../../mcp_config.json) at the workspace root:

```json
{
  "mcpServers": {
    "g-omnios": {
      "command": "python",
      "args": ["-m", "omni_memory.mcp"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

Antigravity IDE discovers this file automatically and registers eager and lazy tools:
- `gomnios_mind4action_cycle`: 4-phase reasoning cycle.
- `omnimemory_track_step`: Persistent LevelDB WAL recording.
- `omnimemory_query_scann`: Dense vector search.
- `gomnios_schedule_persona_skill`: Skill scheduling.
- `gomnios_department_dispatch`: Specialized team delegation.

---

## 🔄 3. Live Glassmorphism Dashboard Callbacks

Antigravity can notify the live G-OmniOS web dashboard during task milestones:

```python
from omni_memory.engine import GOmniOSSystem

system = GOmniOSSystem()
system.step(
    phase="verification",
    title="Invariant Verification Complete",
    thought="All 57 unit tests verified. Out-of-band WAL state consistent.",
    is_milestone=True
)
```
The real-time dashboard at `http://127.0.0.1:8765/` will immediately display an animated toast and update token metrics!
