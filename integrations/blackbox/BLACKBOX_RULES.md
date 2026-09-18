# Blackbox AI Assistant Rules: Google OmniMemory

When operating within a project configured with **Google OmniMemory**:

1. **Avoid Repeating Long Chain-of-Thought History**:
   - Rather than summarizing hundreds of past lines in every response turn, call `omnimemory_track_step` to store raw details in the LevelDB WAL.

2. **Recall via ScaNN Vectors**:
   - Use `omnimemory_query_scann` to search the codebase and past agent reasoning vectors.

3. **Triggering Dashboard Callbacks**:
   - When reaching a milestone, invoke `omnimemory_trigger_callback` with `source="blackbox"`.
   - The user's live dashboard at `http://127.0.0.1:8765/` will display an animated `[BLACKBOX]` cyber-violet badge and focus the active task template (`raft`, `trading`, `refactor`, `research`).
