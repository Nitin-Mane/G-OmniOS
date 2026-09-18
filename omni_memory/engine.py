"""Unified Google OmniMemory System coordinator.

Wires together the Google Open-Source memory ecosystem:
1. Google LevelDB embedded step ledger
2. Google ScaNN vector semantic index
3. Google Diff-Match-Patch context revision engine
4. Google Always-On Memory Agent
5. Google SentencePiece token allocator
"""

from __future__ import annotations
import uuid
import time
from typing import Any, Callable, Dict, List, Optional
from omni_memory.models.step import ProgressStep, StepPhase
from omni_memory.models.memory_tier import MemoryAllocationReport, TierType
from omni_memory.models.context_revision import ContextRevision
from omni_memory.core.diff_patch_engine import GoogleDiffMatchPatch
from omni_memory.core.leveldb_store import LevelDBStepLedger
from omni_memory.core.scann_vector_engine import ScaNNVectorEngine
from omni_memory.core.allocator import MemoryAllocator
from omni_memory.core.tracker import StepTracker
from omni_memory.agents.memory_agent import MemoryAgent
from omni_memory.agents.task_agent import TaskAgent
from omni_memory.core.mind4action import Mind4ActionEngine
from omni_memory.core.firewall_hub import MemoryFirewallHub, DEFAULT_PERSONA_CATALOG
from omni_memory.departments.coordinator import DepartmentCoordinator


TEMPLATES: Dict[str, Dict[str, Any]] = {
    "raft": {
        "id": "raft",
        "title": "Raft Consensus & Distributed State Machine",
        "category": "Distributed Systems",
        "description": "Leader election, heartbeat replication, quorum safety, and log compaction with strict out-of-band step tracking.",
        "prompt": "Build a distributed consensus state machine with Raft election and quorum replication.",
        "system_prompt": "Build a distributed consensus state machine with Raft election and quorum replication.",
        "working_limit": 600,
        "prompt_budget": 600,
        "sample_query": "network partition minority leader",
        "tags": ["consensus", "raft", "distributed-systems", "leveldb"],
        "recommended_phases": ["deliberation", "hypothesis", "planning", "code_gen", "execution", "verification"],
    },
    "trading": {
        "id": "trading",
        "title": "Algorithmic Trading & Risk Parity Strategy",
        "category": "Quantitative Finance",
        "description": "Covariance matrix deconstruction, volatility budgeting, dynamic leverage scaling, and ScaNN rule indexing.",
        "prompt": "Synthesize an algorithmic trading strategy with risk parity constraints and dynamic leverage scaling.",
        "system_prompt": "Synthesize an algorithmic trading strategy with risk parity constraints and dynamic leverage scaling.",
        "working_limit": 800,
        "prompt_budget": 800,
        "sample_query": "volatility targeting rule",
        "tags": ["quant", "risk-parity", "slsqp", "scann"],
        "recommended_phases": ["deliberation", "hypothesis", "planning", "code_gen", "execution", "verification"],
    },
    "refactor": {
        "id": "refactor",
        "title": "Autonomous Code Refactoring & Invariant Synthesis",
        "category": "Software Engineering",
        "description": "Zero-regression codebase modernization, invariant extraction, AST transformation, and Diff-Match-Patch delta auditing.",
        "prompt": "Refactor monolithic agent service into decoupled out-of-band memory micro-architecture with verified invariants.",
        "system_prompt": "Refactor monolithic agent service into decoupled out-of-band memory micro-architecture with verified invariants.",
        "working_limit": 700,
        "prompt_budget": 700,
        "sample_query": "diff match patch myers delta",
        "tags": ["refactoring", "ast", "diff-match-patch", "invariants"],
        "recommended_phases": ["deliberation", "planning", "code_gen", "verification"],
    },
    "research": {
        "id": "research",
        "title": "Multi-Step Scientific & Literature Synthesis",
        "category": "Research & Analysis",
        "description": "High-throughput paper abstraction, cross-source fact distillation, hypothesis generation, and ReasoningBank milestone logging.",
        "prompt": "Synthesize recent advances in decoupled agent memory architectures and context degradation prevention.",
        "system_prompt": "Synthesize recent advances in decoupled agent memory architectures and context degradation prevention.",
        "working_limit": 900,
        "prompt_budget": 900,
        "sample_query": "lost in the middle context degradation",
        "tags": ["research", "reasoning-bank", "synthesis", "knowledge"],
        "recommended_phases": ["deliberation", "hypothesis", "planning", "verification"],
    },
}


class OmniMemorySystem:
    """The fused Google Open-Source memory orchestration system."""

    def __init__(
        self,
        db_path: str = "./.omni_memory_leveldb",
        working_limit: int = 800,
        episodic_limit: int = 3000,
        session_id: Optional[str] = None,
    ):
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # 1. Google Open-Source Core Components
        self.ledger = LevelDBStepLedger(db_path=db_path)
        self.scann = ScaNNVectorEngine(dimension=64)
        self.diff_engine = GoogleDiffMatchPatch()
        self.allocator = MemoryAllocator(
            working_limit=working_limit,
            episodic_limit=episodic_limit,
        )
        self.allocator.set_session_id(self.session_id)
        
        # 2. Out-of-band Tracker
        self.tracker = StepTracker(
            ledger=self.ledger,
            allocator=self.allocator,
            session_id=self.session_id,
        )
        
        # 3. Google Always-On Memory Agent
        self.memory_agent = MemoryAgent(
            allocator=self.allocator,
            scann_engine=self.scann,
            ledger=self.ledger,
            diff_engine=self.diff_engine,
            revision_step_threshold=3,
        )
        
        # Wire tracker listener to Memory Agent
        self.tracker.add_listener(self.memory_agent.on_step_received)
        
        # 4. Primary Task Agent
        self.task_agent = TaskAgent(
            name="OmniTaskAgent",
            tracker=self.tracker,
            allocator=self.allocator,
            memory_agent=self.memory_agent,
        )
        
        # Broadcast listeners for web console / CLI
        self._broadcast_listeners: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # Wire step & revision broadcasting
        self.tracker.add_listener(self._on_step_broadcast)
        self.memory_agent.register_revision_listener(self._on_revision_broadcast)

        # 5. G-OmniOS Cognitive Memory Firewall & Mind4Action Subsystems
        self.mind4action = Mind4ActionEngine()
        self.firewall = MemoryFirewallHub()
        self.departments = DepartmentCoordinator()

    def subscribe(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register a callback for real-time web/CLI broadcasts."""
        self._broadcast_listeners.append(callback)

    def _broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        for cb in self._broadcast_listeners:
            try:
                cb(event_type, data)
            except Exception:
                pass

    def _on_step_broadcast(self, step: ProgressStep) -> None:
        self._broadcast("step_added", {
            "step": step.to_summary_dict(),
            "report": self.allocator.generate_report().model_dump(),
        })

    def _on_revision_broadcast(self, revision: ContextRevision) -> None:
        self._broadcast("context_revised", {
            "revision": revision.model_dump(),
            "report": self.allocator.generate_report().model_dump(),
        })

    def start_task(self, prompt: str) -> None:
        """Start a new task for the primary agent."""
        self.task_agent.set_task(prompt)
        self._broadcast("task_started", {
            "session_id": self.session_id,
            "prompt": prompt,
            "report": self.allocator.generate_report().model_dump(),
        })

    def step(
        self,
        phase: StepPhase,
        title: str,
        thought: str,
        rationale: Optional[str] = None,
        action_type: Optional[str] = None,
        action_payload: Optional[Dict[str, Any]] = None,
        observation: Optional[str] = None,
        is_milestone: bool = False,
        tags: Optional[List[str]] = None,
    ) -> ProgressStep:
        """Execute a step in the primary agent pipeline."""
        return self.task_agent.execute_step(
            phase=phase,
            title=title,
            thought_content=thought,
            thought_rationale=rationale,
            action_type=action_type,
            action_payload=action_payload,
            observation=observation,
            is_milestone=is_milestone,
            tags=tags,
        )

    def force_revision(self) -> Optional[ContextRevision]:
        """Manually trigger the Memory Agent to revise and consolidate context."""
        return self.memory_agent.revise_and_consolidate()

    def query_memory(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform on-demand semantic search using Google ScaNN vector space."""
        return self.memory_agent.query_memory(query=query, top_k=top_k)

    def get_step_by_seq(self, sequence_num: int) -> Optional[ProgressStep]:
        """Fetch a specific historical progress step by sequence number from LevelDB."""
        key = f"steps:{self.session_id}:{sequence_num:08d}"
        raw = self.ledger.get(key)
        if raw:
            return ProgressStep.model_validate(raw)
        steps = self.tracker.get_history()
        for s in steps:
            if s.sequence_num == sequence_num:
                return s
        return None

    def reset(self, new_task_prompt: Optional[str] = None) -> None:
        """Reset the system memory state and start a fresh session."""
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.allocator.clear()
        self.allocator.set_session_id(self.session_id)
        self.tracker.reset(self.session_id)
        self.memory_agent.reset()
        
        prompt = new_task_prompt or "New task initialized."
        self.task_agent.set_task(prompt)
        self._broadcast("task_started", {
            "session_id": self.session_id,
            "prompt": prompt,
            "report": self.allocator.generate_report().model_dump(),
        })

    def get_templates(self) -> List[Dict[str, Any]]:
        """Return list of available agent memory templates."""
        return list(TEMPLATES.values())

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Fetch template by identifier."""
        return TEMPLATES.get(template_id.lower())

    def trigger_callback(
        self,
        event_name: str,
        template_id: Optional[str] = None,
        source: str = "cli",
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Trigger an out-of-band callback event from CLI or VS Code.
        
        Broadcasts the callback to the WebApp via SSE, syncing the related
        template, state updates, and telemetry.
        """
        payload = payload or {}
        template_info = self.get_template(template_id) if template_id else None
        
        # If template provided and task not configured, apply template prompt
        if template_info and payload.get("apply_prompt", False):
            self.task_agent.set_task(template_info["prompt"])

        # If payload specifies a step to record out-of-band
        step_recorded = None
        if payload.get("step_title"):
            phase_str = payload.get("step_phase", "execution")
            try:
                phase = StepPhase(phase_str)
            except ValueError:
                phase = StepPhase.EXECUTION
            st = self.step(
                phase=phase,
                title=payload["step_title"],
                thought=payload.get("step_thought", f"Callback step from {source}"),
                observation=payload.get("step_observation", "Verified callback payload."),
                is_milestone=payload.get("is_milestone", False),
            )
            step_recorded = st.to_summary_dict()

        callback_event = {
            "status": "callback_received",
            "callback_id": f"cb_{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "event_name": event_name,
            "event": event_name,
            "source": source,  # "vscode" or "cli"
            "template_id": template_id,
            "template": template_info,
            "payload": payload,
            "step": step_recorded,
            "session_id": self.session_id,
            "report": self.allocator.generate_report().model_dump(),
        }

        self._broadcast("callback_triggered", callback_event)
        return callback_event

    def mind4action_cycle(self, stimulus: str) -> Dict[str, Any]:
        """Execute a 4-phase Mind4Action cognitive turn: Perceive -> Reflect -> Intend -> Act."""
        # 1. ScaNN semantic affinity
        scann_results = self.scann.search(stimulus, top_k=2)

        # 2. Firewall prompt inspection
        inspection = self.firewall.inspect_prompt(stimulus, self.mind4action.state)

        # 3. Drive the 4-stage cognitive engine
        turn = self.mind4action.run_cycle(
            stimulus=stimulus,
            scann_results=scann_results,
            firewall_inspection=inspection,
            system_step_fn=self.step
        )

        turn_dict = turn.model_dump()
        self._broadcast("mind4action_turn", turn_dict)
        return turn_dict

    def inspect_firewall(self, text: str) -> Dict[str, Any]:
        """Inspect context via the Cognitive Memory Firewall Hub."""
        raw_res = self.firewall.inspect_prompt(text, self.mind4action.state)
        blocked = raw_res.get("blocked", False)
        rule = raw_res.get("rule", "pass")
        return {
            "verdict": "BLOCKED" if blocked else "ALLOWED",
            "blocked": blocked,
            "triggered_rules": [rule] if rule and rule != "pass" else [],
            "reason": raw_res.get("reason"),
            "suggested_mitigation": raw_res.get("reason") if blocked else "Context verified compliant with G-OmniOS invariants.",
            "clean_context": text if not blocked else f"[SHIELDED TO LEVELDB WAL: {raw_res.get('shielded_tokens', 0)} tokens]",
            "shielded_tokens": raw_res.get("shielded_tokens", 0),
            "allocated_budget": raw_res.get("allocated_budget", 700)
        }

    def schedule_persona_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Schedule and activate a persona skill from the Technical, Social, or Mental track."""
        skill = self.firewall.schedule_skill(skill_id)
        if skill:
            self.task_agent.set_task(skill.system_prompt)
            skill_dict = skill.model_dump()
            self._broadcast("skill_scheduled", skill_dict)
            return skill_dict
        return None

    def dispatch_department(
        self,
        department: str,
        task: str = "status",
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dispatch an operational inquiry or directive to an organizational agent team."""
        data = payload or {}
        data.setdefault("telemetry", self.get_telemetry())
        data.setdefault("cognitive_state", self.mind4action.state)
        res = self.departments.dispatch(department=department, task=task, payload=data)
        self._broadcast("department_update", {"department": department, "task": task, "result": res})
        return res

    def get_cognitive_telemetry(self) -> Dict[str, Any]:
        """Fetch real-time cognitive state, psychological behavior, and firewall status."""
        return {
            "cognitive_state": self.mind4action.state.to_dict(),
            "firewall": self.firewall.get_firewall_status(),
            "recent_mind4action_turns": self.mind4action.get_recent_turns(limit=5),
            "department_roster": self.departments.get_team_roster(),
        }

    def get_telemetry(self) -> Dict[str, Any]:
        """Fetch real-time memory metrics, allocations, and token savings."""
        report = self.allocator.generate_report()
        steps = self.tracker.get_history()
        prompt_info = self.task_agent.get_current_prompt_window()
        revisions = self.memory_agent.get_revision_history()

        return {
            "session_id": self.session_id,
            "report": report.model_dump(),
            "prompt_window": prompt_info,
            "canonical_context": self.memory_agent.get_canonical_context(),
            "step_count": len(steps),
            "recent_steps": [s.to_summary_dict() for s in steps[-25:]],
            "recent_revisions": [r.model_dump() for r in revisions[-10:]],
            "scann_index_size": self.scann.count(),
            "templates": self.get_templates(),
            "cognitive_state": self.mind4action.state.to_dict(),
            "firewall": self.firewall.get_firewall_status(),
            "recent_mind4action": self.mind4action.get_recent_turns(limit=5),
            "department_roster": self.departments.get_team_roster(),
            "persona_catalog": self.firewall.get_catalog_by_track(),
        }


# Universal G-OmniOS System Alias
GOmniOSSystem = OmniMemorySystem
