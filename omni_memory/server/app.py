"""Lightweight, zero-dependency embedded server for Google OmniMemory.

Serves the Glassmorphism real-time web console and exposes REST + SSE
endpoints for live memory allocation telemetry and step streaming.
"""

from __future__ import annotations
import os
import json
import time
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from omni_memory.engine import OmniMemorySystem
from omni_memory.models.step import StepPhase


STATIC_DIR = Path(__file__).parent / "static"


class OmniMemoryHTTPHandler(SimpleHTTPRequestHandler):
    """Handles REST and static requests for the OmniMemory web dashboard."""

    system: OmniMemorySystem = None
    subscribers = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            telemetry = self.system.get_telemetry()
            self.wfile.write(json.dumps(telemetry, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed.path in ("/api/query", "/api/search"):
            qs = parse_qs(parsed.query)
            query_str = qs.get("q", qs.get("query", [""]))[0]
            top_k = int(qs.get("top_k", [5])[0])
            results = self.system.query_memory(query=query_str, top_k=top_k) if query_str else []
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"query": query_str, "top_k": top_k, "results": results}).encode("utf-8"))
            return

        elif parsed.path == "/api/templates":
            qs = parse_qs(parsed.query)
            t_id = qs.get("id", [None])[0]
            if t_id:
                t = self.system.get_template(t_id)
                if t:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps(t).encode("utf-8"))
                    return
                self.send_response(404)
                self.end_headers()
                return
            templates_list = self.system.get_templates()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "templates": templates_list,
                "count": len(templates_list)
            }).encode("utf-8"))
            return

        elif parsed.path == "/api/cognitive":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(self.system.get_cognitive_telemetry()).encode("utf-8"))
            return

        elif parsed.path == "/api/firewall/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(self.system.firewall.get_firewall_status()).encode("utf-8"))
            return

        elif parsed.path in ("/api/skills/catalog", "/api/skills"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(self.system.firewall.get_catalog_by_track()).encode("utf-8"))
            return

        elif parsed.path == "/api/departments":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(self.system.departments.get_team_roster()).encode("utf-8"))
            return

        elif parsed.path == "/api/step":
            qs = parse_qs(parsed.query)
            seq_str = qs.get("seq", [None])[0]
            if seq_str and seq_str.isdigit():
                step = self.system.get_step_by_seq(int(seq_str))
                if step:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps(step.model_dump()).encode("utf-8"))
                    return
            self.send_response(404)
            self.end_headers()
            return

        elif parsed.path == "/api/events":
            # Server-Sent Events (SSE) stream for live updates
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            client_queue = []
            lock = threading.Lock()

            def listener(event_type: str, data: dict):
                with lock:
                    client_queue.append((event_type, data))

            self.system.subscribe(listener)

            try:
                # Send initial state
                initial = json.dumps(self.system.get_telemetry())
                self.wfile.write(f"event: initial_state\ndata: {initial}\n\n".encode("utf-8"))
                self.wfile.flush()

                while True:
                    time.sleep(0.3)
                    with lock:
                        items = list(client_queue)
                        client_queue.clear()

                    for ev_type, ev_data in items:
                        msg = f"event: {ev_type}\ndata: {json.dumps(ev_data)}\n\n"
                        self.wfile.write(msg.encode("utf-8"))
                        self.wfile.flush()
            except (ConnectionResetError, BrokenPipeError):
                pass
            return

        # Serve static dashboard files
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            payload = {}

        if parsed.path == "/api/step":
            phase_str = payload.get("phase", "deliberation")
            try:
                phase = StepPhase(phase_str)
            except ValueError:
                phase = StepPhase.DELIBERATION

            step = self.system.step(
                phase=phase,
                title=payload.get("title", "Custom Step"),
                thought=payload.get("thought", "Thinking through sub-problem..."),
                observation=payload.get("observation"),
                is_milestone=payload.get("is_milestone", False),
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(step.to_summary_dict()).encode("utf-8"))
            return

        elif parsed.path in ("/api/query", "/api/search"):
            query_str = payload.get("query", payload.get("q", ""))
            top_k = int(payload.get("top_k", 5))
            results = self.system.query_memory(query=query_str, top_k=top_k) if query_str else []
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"query": query_str, "top_k": top_k, "results": results}).encode("utf-8"))
            return

        elif parsed.path == "/api/callback":
            event_name = payload.get("event", payload.get("event_name", "agent_callback"))
            template_id = payload.get("template", payload.get("template_id"))
            source = payload.get("source", "cli")
            cb_payload = payload.get("payload", payload)

            cb_event = self.system.trigger_callback(
                event_name=event_name,
                template_id=template_id,
                source=source,
                payload=cb_payload,
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(cb_event).encode("utf-8"))
            return

        elif parsed.path == "/api/reset":
            prompt = payload.get("prompt", "Architecting an autonomous memory agent using Google open-source tools.")
            self.system.reset(new_task_prompt=prompt)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "reset_successful",
                "session_id": self.system.session_id,
                "telemetry": self.system.get_telemetry(),
            }).encode("utf-8"))
            return

        elif parsed.path == "/api/revise":
            rev = self.system.force_revision()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            resp = rev.model_dump() if rev else {"status": "no_unrevised_steps"}
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        elif parsed.path == "/api/simulate":
            # Run a simulated reasoning sequence in background thread
            threading.Thread(target=self._run_simulation, daemon=True).start()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "simulation_started"}).encode("utf-8"))
            return

        elif parsed.path == "/api/mind4action":
            stimulus = payload.get("stimulus", payload.get("prompt", ""))
            turn = self.system.mind4action_cycle(stimulus)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(turn).encode("utf-8"))
            return

        elif parsed.path == "/api/firewall/inspect":
            text = payload.get("text", payload.get("prompt", ""))
            inspection = self.system.inspect_firewall(text)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(inspection).encode("utf-8"))
            return

        elif parsed.path == "/api/skills/schedule":
            skill_id = payload.get("skill_id", payload.get("id", ""))
            scheduled = self.system.schedule_persona_skill(skill_id)
            self.send_response(200 if scheduled else 404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(scheduled or {"error": f"Skill '{skill_id}' not found"}).encode("utf-8"))
            return

        elif parsed.path == "/api/department/dispatch":
            dept = payload.get("department", "manager")
            task = payload.get("task", "status")
            res = self.system.dispatch_department(dept, task, payload)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def _run_simulation(self):
        """Simulate a realistic 6-step problem-solving trajectory."""
        sim_steps = [
            (StepPhase.DELIBERATION, "Deconstruct Architecture Constraints", "Evaluating out-of-band memory requirements against LLM prompt token limits. LevelDB WAL handles durable persistence, Diff-Match-Patch handles context revision deltas.", "Token growth must be bounded strictly under 800 tokens."),
            (StepPhase.HYPOTHESIS, "Formulate Multi-Tier Allocation Strategy", "If we route volatile thoughts to LevelDB WAL and only pass distilled deltas into the working prompt, attention degradation is eliminated.", "Hypothesis: Token savings will exceed 80%."),
            (StepPhase.PLANNING, "Draft ScaNN Vector Space Partitioning", "Designing 64-dimensional dense projection index to partition memory slots into Voronoi buckets for O(1) top-k lookup.", "Index structure partitioned into 4 clusters."),
            (StepPhase.CODE_GEN, "Implement Diff-Match-Patch Delta Synthesis", "Writing Myers diff algorithm integration to compute diff deltas between consecutive memory states.", "Patch generator produces semantic diff chunks."),
            (StepPhase.EXECUTION, "Run Stress Test with 20 Reasoning Loops", "Benchmarking memory allocation governor under rapid step generation.", "Memory Allocator held prompt context constant at ~420 tokens."),
            (StepPhase.VERIFICATION, "Verify Memory Context Integrity & Recall", "Testing ScaNN vector recall on 'LevelDB WAL durable persistence'. Recall score: 0.94.", "Verified: Memory Agent correctly consolidated context with zero prompt bloat."),
        ]

        for phase, title, thought, obs in sim_steps:
            time.sleep(1.2)
            self.system.step(
                phase=phase,
                title=title,
                thought=thought,
                observation=obs,
                is_milestone=(phase in (StepPhase.HYPOTHESIS, StepPhase.VERIFICATION)),
            )


def run_dashboard_server(
    system: Optional[OmniMemorySystem] = None,
    port: int = 8765,
    open_browser: bool = False,
) -> HTTPServer:
    """Start the embedded dashboard web server."""
    if system is None:
        system = OmniMemorySystem()
        system.start_task("Architecting an autonomous memory agent using Google open-source tools.")

    OmniMemoryHTTPHandler.system = system
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, OmniMemoryHTTPHandler)
    url = f"http://127.0.0.1:{port}/"
    print(f"[*] Google OmniMemory Dashboard running at: {url}")

    if open_browser:
        try:
            import webbrowser
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        except Exception:
            pass

    return httpd
