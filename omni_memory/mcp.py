"""Model Context Protocol (MCP) Server for Google OmniMemory.

Implements a standard JSON-RPC 2.0 stdio server compliant with the MCP specification.
Compatible with Google Antigravity, Anthropic Claude (Desktop & Code), OpenCode,
and Blackbox AI.
"""

from __future__ import annotations
import sys
import json
import traceback
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from omni_memory.engine import OmniMemorySystem, TEMPLATES
from omni_memory.models.step import StepPhase


# Global instance of OmniMemorySystem for this MCP process
_system: Optional[OmniMemorySystem] = None


def get_system() -> OmniMemorySystem:
    global _system
    if _system is None:
        _system = OmniMemorySystem()
        _system.start_task("Autonomous agent task via Model Context Protocol.")
    return _system


TOOLS_DEFINITION = [
    {
        "name": "omnimemory_track_step",
        "description": "Log an intermediate thought, reasoning deliberation, or execution step out-of-band into Google LevelDB WAL. Shields tokens from LLM prompt window to guarantee zero prompt bloat.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Concise summary of the reasoning or execution step (e.g. 'Analyze Covariance Matrix')."
                },
                "thought": {
                    "type": "string",
                    "description": "Detailed out-of-band thoughts, hypotheses, mathematical calculations, or scratch notes."
                },
                "observation": {
                    "type": "string",
                    "description": "Results, outputs, or verified facts resulting from this step."
                },
                "phase": {
                    "type": "string",
                    "enum": ["deliberation", "hypothesis", "planning", "code_gen", "execution", "verification"],
                    "default": "deliberation",
                    "description": "Current reasoning lifecycle phase."
                },
                "is_milestone": {
                    "type": "boolean",
                    "default": False,
                    "description": "Mark true if this step establishes a major ReasoningBank strategic milestone."
                }
            },
            "required": ["title", "thought"]
        }
    },
    {
        "name": "omnimemory_query_scann",
        "description": "Query Google ScaNN dense vector memory for on-demand semantic recall of past thoughts, strategy rules, or invariants without loading full history into the prompt window.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language or keyword search query (e.g. 'volatility rule', 'LevelDB WAL', 'network partition')."
                },
                "top_k": {
                    "type": "integer",
                    "default": 3,
                    "description": "Number of nearest neighbor memory slots to retrieve."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "omnimemory_trigger_callback",
        "description": "Trigger an OmniMemory callback event to synchronize the real-time Glassmorphism dashboard webapp and focus a related ReasoningBank template (raft, trading, refactor, research). Compatible with Antigravity, Claude, ChatGPT, OpenCode, and Blackbox.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "enum": ["raft", "trading", "refactor", "research"],
                    "description": "ReasoningBank task template to activate on the webapp dashboard."
                },
                "source": {
                    "type": "string",
                    "enum": ["antigravity", "claude", "chatgpt", "codex", "opencode", "blackbox", "vscode", "cli"],
                    "default": "antigravity",
                    "description": "Originating agent or IDE platform."
                },
                "message": {
                    "type": "string",
                    "description": "Reasoning context or milestone description for the dashboard toast."
                },
                "step_title": {
                    "type": "string",
                    "description": "Optional step title to record in LevelDB simultaneously."
                },
                "dashboard_port": {
                    "type": "integer",
                    "default": 8765,
                    "description": "Port of the local OmniMemory dashboard server."
                }
            },
            "required": ["template_id"]
        }
    },
    {
        "name": "omnimemory_get_template",
        "description": "Retrieve the prompt definition, bounded token budget, and sample query for a ReasoningBank task template.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "template_id": {
                    "type": "string",
                    "enum": ["raft", "trading", "refactor", "research"],
                    "description": "The template identifier to retrieve."
                }
            },
            "required": ["template_id"]
        }
    },
    {
        "name": "omnimemory_revise_context",
        "description": "Trigger the Google Always-On Memory Agent to compute a Diff-Match-Patch Myers delta revision, consolidating unrevised steps into a compact state update.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "omnimemory_get_telemetry",
        "description": "Get real-time token savings metrics, active prompt load, and LevelDB WAL step counts.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "gomnios_mind4action_cycle",
        "description": "Execute a 4-stage Mind4Action cognitive activity cycle (Perceive -> Reflect -> Intend -> Act). Assesses psychological state, deliberate thought depth, and executes actions out-of-band.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "stimulus": {
                    "type": "string",
                    "description": "The incoming user instruction, goal, or external stimulus to process."
                }
            },
            "required": ["stimulus"]
        }
    },
    {
        "name": "gomnios_firewall_inspect",
        "description": "Inspect prompt context against the G-OmniOS Cognitive Memory Firewall to prevent cognitive overload, psychological leaks, and context degradation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text or prompt context to inspect against firewall invariants."
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "gomnios_schedule_persona_skill",
        "description": "Schedule a persona-building skill from the G-OmniOS catalog across Technical, Social, or Mental ability tracks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill_id": {
                    "type": "string",
                    "description": "The identifier of the persona skill (e.g. 'tech_distributed_consensus', 'social_collaborative_synthesis', 'mental_cognitive_resilience')."
                }
            },
            "required": ["skill_id"]
        }
    },
    {
        "name": "gomnios_department_dispatch",
        "description": "Dispatch a task or strategic inquiry to a G-OmniOS organizational agent department (Manager, HR, Fullstack AI, Catalog, Marketing, DevOps).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "enum": ["manager", "hr", "fullstack", "catalog", "marketing", "devops"],
                    "description": "Target agent department team."
                },
                "task": {
                    "type": "string",
                    "default": "status",
                    "description": "Operation or task to request from the department."
                },
                "payload": {
                    "type": "object",
                    "description": "Optional parameters or context data for the department agent."
                }
            },
            "required": ["department"]
        }
    },
    {
        "name": "gomnios_get_cognitive_status",
        "description": "Retrieve live cognitive load index (CLI), flow score, psychological behavior, and firewall status.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    system = get_system()

    if name == "omnimemory_track_step":
        phase_str = arguments.get("phase", "deliberation")
        try:
            phase = StepPhase(phase_str)
        except ValueError:
            phase = StepPhase.DELIBERATION

        step = system.step(
            phase=phase,
            title=arguments["title"],
            thought=arguments["thought"],
            observation=arguments.get("observation"),
            is_milestone=arguments.get("is_milestone", False),
        )
        summary = step.to_summary_dict()
        return {
            "status": "success",
            "step_id": step.step_id,
            "sequence_num": step.sequence_num,
            "phase": step.phase.value,
            "tokens_shielded": step.token_weight,
            "wal_key": summary["wal_key"],
            "message": f"Step #{step.sequence_num} recorded out-of-band to LevelDB WAL (+{step.token_weight} tokens shielded)."
        }

    elif name == "omnimemory_query_scann":
        query = arguments.get("query", "")
        top_k = int(arguments.get("top_k", 3))
        results = system.query_memory(query=query, top_k=top_k)
        return {
            "query": query,
            "count": len(results),
            "results": results
        }

    elif name == "omnimemory_trigger_callback":
        template_id = arguments.get("template_id", "raft")
        source = arguments.get("source", "antigravity")
        message = arguments.get("message") or f"Callback triggered from {source} with template '{template_id}'"
        step_title = arguments.get("step_title")
        port = int(arguments.get("dashboard_port", 8765))

        # Local system trigger
        cb_res = system.trigger_callback(
            event_name=f"{source.title()} Callback",
            template_id=template_id,
            source=source,
            payload={"message": message, "step_title": step_title}
        )

        # Notify running HTTP server if alive
        server_notified = False
        try:
            http_url = f"http://127.0.0.1:{port}/api/callback"
            req = urllib.request.Request(
                http_url,
                data=json.dumps({
                    "event": f"{source.title()} Callback Event",
                    "template_id": template_id,
                    "source": source,
                    "payload": {"message": message, "step_title": step_title}
                }).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    server_notified = True
        except Exception:
            server_notified = False

        template_info = TEMPLATES.get(template_id, {})
        return {
            "status": "callback_triggered",
            "source": source,
            "template_id": template_id,
            "template_title": template_info.get("title"),
            "prompt_budget": template_info.get("prompt_budget"),
            "server_notified": server_notified,
            "dashboard_url": f"http://127.0.0.1:{port}/?template={template_id}&source={source}",
            "message": f"Callback executed for {source}. Dashboard synchronized with template '{template_id}'."
        }

    elif name == "omnimemory_get_template":
        t_id = arguments.get("template_id", "raft")
        tpl = TEMPLATES.get(t_id)
        if not tpl:
            return {"error": f"Template '{t_id}' not found. Available: {list(TEMPLATES.keys())}"}
        return tpl

    elif name == "omnimemory_revise_context":
        rev = system.force_revision()
        if rev:
            return {
                "status": "revised",
                "revision_id": rev.revision_id,
                "compression_ratio": rev.compression_ratio,
                "revised_tokens": rev.revised_tokens,
                "patch_delta": rev.patch_delta
            }
        return {"status": "no_unrevised_steps", "message": "All steps already consolidated."}

    elif name == "omnimemory_get_telemetry":
        return system.get_telemetry()

    elif name == "gomnios_mind4action_cycle":
        stimulus = arguments.get("stimulus", "")
        turn = system.mind4action_cycle(stimulus)
        turn_id = turn.get("turn_id", "")
        return {
            "status": "success",
            "cycle": turn,
            "message": f"Mind4Action cycle #{turn_id} completed: Perceive -> Reflect -> Intend -> Act"
        }

    elif name == "gomnios_firewall_inspect":
        text = arguments.get("text", "")
        res = system.inspect_firewall(text)
        return {
            "status": "success",
            "inspection": res
        }

    elif name == "gomnios_schedule_persona_skill":
        skill_id = arguments.get("skill_id", "")
        res = system.schedule_persona_skill(skill_id)
        return res

    elif name == "gomnios_department_dispatch":
        dept = arguments.get("department", "manager")
        task = arguments.get("task", "status")
        payload = arguments.get("payload")
        res = system.dispatch_department(dept, task, payload)
        return res

    elif name == "gomnios_get_cognitive_status":
        return {
            "status": "success",
            "cognitive_telemetry": system.get_cognitive_telemetry()
        }

    else:
        raise ValueError(f"Unknown tool: {name}")


def process_jsonrpc_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "google-omnimemory",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        # Notification - no response
        return None

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    elif method in ("tools/list", "tools/listTools"):
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS_DEFINITION
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            result_data = handle_tool_call(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result_data, indent=2)
                        }
                    ],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing {tool_name}: {str(e)}\n{traceback.format_exc()}"
                        }
                    ],
                    "isError": True
                }
            }

    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": [
                    {
                        "uri": "omnimemory://telemetry",
                        "name": "OmniMemory Live Telemetry",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "omnimemory://templates",
                        "name": "ReasoningBank Task Templates",
                        "mimeType": "application/json"
                    }
                ]
            }
        }

    elif method == "resources/read":
        uri = params.get("uri")
        if uri == "omnimemory://telemetry":
            content = json.dumps(get_system().get_telemetry(), indent=2)
        elif uri == "omnimemory://templates":
            content = json.dumps(list(TEMPLATES.values()), indent=2)
        else:
            content = json.dumps({"error": f"Unknown resource: {uri}"})
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": content
                    }
                ]
            }
        }

    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
        return None


def send_response(resp: Dict[str, Any]):
    line = json.dumps(resp)
    # Stdio transport sends a single JSON line
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def run_stdio_mcp():
    """Main loop for MCP JSON-RPC stdio protocol."""
    # Ensure stdout is in line-buffered mode
    sys.stderr.write("[Google OmniMemory MCP Server] Ready on stdio.\n")
    sys.stderr.flush()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            # Check if using Content-Length header format
            if line.lower().startswith("content-length:"):
                length = int(line.split(":")[1].strip())
                # Read empty line
                sys.stdin.readline()
                body = sys.stdin.read(length)
                req = json.loads(body)
            else:
                req = json.loads(line)

            resp = process_jsonrpc_request(req)
            if resp is not None:
                send_response(resp)

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            sys.stderr.write(f"[MCP Server Error] {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    run_stdio_mcp()
