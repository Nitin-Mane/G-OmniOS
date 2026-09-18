"""OpenAI and Codex Integration Adapter for Google OmniMemory.

Enables OpenAI Python client executions (GPT-4o, o1, Codex) to route tool calls,
intermediate deliberations, and execution traces out-of-band into OmniMemory.
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from omni_memory.engine import OmniMemorySystem
from omni_memory.models.step import StepPhase


class OmniMemoryOpenAIAdapter:
    """Helper for executing OmniMemory tools dispatched by OpenAI or Codex models."""

    def __init__(self, system: Optional[OmniMemorySystem] = None, source: str = "chatgpt"):
        self.system = system or OmniMemorySystem()
        self.source = source

    def execute_tool_call(self, tool_name: str, arguments_json: str | dict) -> Dict[str, Any]:
        """Execute a tool call emitted by OpenAI `tool_calls` response."""
        if isinstance(arguments_json, str):
            args = json.loads(arguments_json)
        else:
            args = arguments_json

        if tool_name == "omnimemory_track_step":
            phase_str = args.get("phase", "deliberation")
            try:
                phase = StepPhase(phase_str)
            except ValueError:
                phase = StepPhase.DELIBERATION

            step = self.system.step(
                phase=phase,
                title=args["title"],
                thought=args["thought"],
                observation=args.get("observation"),
                is_milestone=args.get("is_milestone", False),
            )
            return {
                "status": "success",
                "step_id": step.step_id,
                "sequence_num": step.sequence_num,
                "tokens_shielded": step.token_weight,
                "message": f"Recorded step #{step.sequence_num} out-of-band to LevelDB WAL."
            }

        elif tool_name == "omnimemory_query_scann":
            query = args.get("query", "")
            top_k = int(args.get("top_k", 3))
            results = self.system.query_memory(query=query, top_k=top_k)
            return {"query": query, "results": results}

        elif tool_name == "omnimemory_trigger_callback":
            template_id = args.get("template_id", "raft")
            source = args.get("source", self.source)
            msg = args.get("message") or f"{source.upper()} triggered callback for template {template_id}"
            step_title = args.get("step_title")

            cb_event = self.system.trigger_callback(
                event_name=f"{source.title()} Execution Callback",
                template_id=template_id,
                source=source,
                payload={"message": msg, "step_title": step_title}
            )
            return {
                "status": "callback_triggered",
                "source": source,
                "template_id": template_id,
                "dashboard_url": f"http://127.0.0.1:8765/?template={template_id}&source={source}",
                "event": cb_event
            }

        else:
            return {"error": f"Unknown OmniMemory tool: {tool_name}"}
