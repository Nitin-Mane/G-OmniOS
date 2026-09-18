# Claude Desktop & Agent Guidelines: G-OmniOS Integration

When executing reasoning, architectural synthesis, long research tasks, or code generation workflows, Claude has access to the **G-OmniOS** suite:

### 1. Zero-Token Memory Logging (`omnimemory_track_step`)
- Call this tool to store verbose scratchpad calculations, hypothesis validations, and intermediate execution logs out-of-band into the Google LevelDB WAL.
- This keeps your active prompt token count strictly flat and prevents context degradation.

### 2. Semantic Memory Retrieval (`omnimemory_query_scann`)
- Query past decisions, architectural patterns, and project rules using Google ScaNN dense vector embeddings instead of asking the user to repeat past context.

### 3. Mind4Action Cognitive Cycle (`gomnios_mind4action_cycle`)
- Run a structured 4-phase reasoning cycle (`Perceive -> Reflect -> Intend -> Act`) to evaluate task complexity, deliberation depth, and formulate clear intentions.

### 4. Context Governor & Prompt Optimization (`gomnios_context_inspect` / `gomnios_firewall_inspect`)
- Inspect incoming user prompts to optimize context, balance cognitive load, and eliminate bloat.

### 5. Multi-Disciplinary Agent Dispatch (`gomnios_department_dispatch`)
- Delegate specialized sub-tasks to organizational agents: `manager`, `hr`, `fullstack`, `catalog`, `marketing`, or `devops`.

### 6. Live Dashboard Synchronization (`omnimemory_trigger_callback`)
- When initiating or concluding a task matching one of the ReasoningBank blueprints (`raft`, `trading`, `refactor`, `research`), trigger this tool with `source="claude"`.
- The user will immediately see an animated `[CLAUDE]` toast on their live Glassmorphism console (`http://127.0.0.1:8765/`).
