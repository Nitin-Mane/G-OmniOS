"""Mind4Action Cognitive Engine for G-OmniOS.

Executes the four-stage cognitive activity cycle:
  Perceive -> Reflect -> Intend -> Act
Tracks thinking patterns, psychological behaviors, and deliberate action synthesis.
"""

from __future__ import annotations
import time
import math
from typing import Any, Dict, List, Optional
from omni_memory.models.cognitive_profile import (
    AbilityTrack,
    CognitivePattern,
    PsychologicalBehavior,
    Mind4ActionPhase,
    CognitiveState,
    Mind4ActionTurn,
)
from omni_memory.models.step import StepPhase


class Mind4ActionEngine:
    """Orchestrates cognitive activity and psychological state assessment."""

    def __init__(self):
        self.state = CognitiveState()
        self.history: List[Mind4ActionTurn] = []
        self._turn_counter = 0

    def perceive(self, stimulus: str) -> Dict[str, Any]:
        """Stage 1: Perceive - Ingest and normalize input stimulus."""
        cleaned = stimulus.strip()
        tokens_est = max(1, len(cleaned.split()))
        complexity = min(1.0, tokens_est / 60.0)

        # Classify perceived ability tracks
        tracks = [AbilityTrack.TECHNICAL]
        lower_txt = cleaned.lower()
        if any(w in lower_txt for w in ["team", "consensus", "review", "stakeholder", "collaborate", "social", "briefing"]):
            tracks.append(AbilityTrack.SOCIAL)
        if any(w in lower_txt for w in ["stress", "calm", "outage", "fatigue", "pressure", "resilience", "mental", "focus"]):
            tracks.append(AbilityTrack.MENTAL)

        return {
            "raw_stimulus": cleaned,
            "estimated_tokens": tokens_est,
            "token_estimate": tokens_est,
            "stimulus_complexity": round(complexity, 2),
            "tracks": tracks,
            "timestamp": time.time(),
        }

    def reflect(self, perceived: Dict[str, Any], scann_results: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Stage 2: Reflect - Analyze cognitive patterns and psychological behaviors."""
        text = perceived["raw_stimulus"].lower()
        complexity = perceived["stimulus_complexity"]

        # Behavioral heuristics based on semantic markers and interaction cadence
        fatigue_markers = ["tired", "stuck", "again", "repeat", "why is this failing", "confused", "give up"]
        analytical_markers = ["calculate", "invariant", "matrix", "architecture", "verify", "optimize", "proof"]
        creative_markers = ["explore", "brainstorm", "design", "imagine", "novel", "alternative"]
        social_markers = ["collaborate", "team", "communicate", "explain", "stakeholder", "consensus"]

        # Classify pattern
        if any(m in text for m in analytical_markers):
            pattern = CognitivePattern.ANALYTICAL
        elif any(m in text for m in creative_markers):
            pattern = CognitivePattern.DIVERGENT
        elif any(m in text for m in social_markers):
            pattern = CognitivePattern.CONVERGENT
        elif complexity > 0.7:
            pattern = CognitivePattern.SYSTEMATIC
        else:
            pattern = CognitivePattern.INTUITIVE

        # Classify psychological behavior
        if any(m in text for m in fatigue_markers):
            behavior = PsychologicalBehavior.FATIGUE
            cli = min(1.0, self.state.cognitive_load_index + 0.20)
            flow = max(0.1, self.state.flow_score - 0.25)
            stress = min(1.0, self.state.stress_indicator + 0.20)
        elif pattern == CognitivePattern.ANALYTICAL:
            behavior = PsychologicalBehavior.DELIBERATE
            cli = min(0.85, self.state.cognitive_load_index + 0.05)
            flow = min(0.95, self.state.flow_score + 0.05)
            stress = max(0.05, self.state.stress_indicator - 0.05)
        elif pattern == CognitivePattern.DIVERGENT:
            behavior = PsychologicalBehavior.EXPLORATION
            cli = max(0.2, self.state.cognitive_load_index - 0.05)
            flow = min(0.90, self.state.flow_score + 0.10)
            stress = max(0.05, self.state.stress_indicator - 0.05)
        elif pattern == CognitivePattern.CONVERGENT:
            behavior = PsychologicalBehavior.FLOW
            cli = max(0.2, self.state.cognitive_load_index - 0.02)
            flow = min(0.95, self.state.flow_score + 0.08)
            stress = max(0.05, self.state.stress_indicator - 0.05)
        else:
            behavior = PsychologicalBehavior.FLOW
            cli = self.state.cognitive_load_index
            flow = self.state.flow_score
            stress = self.state.stress_indicator

        # Update persistent state
        self.state.cognitive_load_index = round(cli, 2)
        self.state.flow_score = round(flow, 2)
        self.state.stress_indicator = round(stress, 2)
        self.state.deliberation_depth = round(complexity * 3.5, 2)
        self.state.primary_pattern = pattern
        self.state.active_behavior = behavior
        self.state.last_updated = time.time()

        memory_affinity = 0.0
        if scann_results:
            top_relevance = max((r.get("relevance", 0.0) for r in scann_results), default=0.0)
            memory_affinity = round(top_relevance, 3)

        tracks_perceived = [t.value for t in perceived.get("tracks", [AbilityTrack.TECHNICAL])]

        return {
            "cognitive_pattern": pattern.value,
            "psychological_behavior": behavior.value,
            "cli": self.state.cognitive_load_index,
            "cognitive_load_index": self.state.cognitive_load_index,
            "flow_score": self.state.flow_score,
            "deliberation_depth": self.state.deliberation_depth,
            "stress_level": self.state.stress_indicator,
            "memory_affinity": memory_affinity,
            "tracks_perceived": tracks_perceived,
            "insights": f"Detected {pattern.value.upper()} thinking in {behavior.value.upper()} psychological state."
        }

    def intend(self, perceived: Dict[str, Any], reflection: Dict[str, Any], firewall_inspection: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 3: Intend - Apply firewall rules, formulate bounded intention."""
        behavior = reflection["psychological_behavior"]
        pattern = reflection["cognitive_pattern"]
        is_blocked = firewall_inspection.get("blocked", False)

        if is_blocked:
            target_action = "shield_and_recover"
            rationale = f"Firewall blocked prompt: {firewall_inspection.get('reason')}. Activating cognitive safeguard."
        elif behavior == PsychologicalBehavior.FATIGUE.value:
            target_action = "breakdown_and_consolidate"
            rationale = "User showing cognitive fatigue markers. Downscaling complexity and consolidating past memory."
        elif pattern == CognitivePattern.ANALYTICAL.value:
            target_action = "deep_deliberation_wal"
            rationale = "High analytical complexity. Logging scratchpad out-of-band into LevelDB to protect working context."
        else:
            target_action = "execute_scheduled_skill"
            rationale = "Clear cognitive flow state. Ready for persona skill execution."

        return {
            "target_action": target_action,
            "rationale": rationale,
            "prompt_budget_allocated": firewall_inspection.get("allocated_budget", 700),
            "firewall_passed": not is_blocked,
            "timestamp": time.time(),
        }

    def act(
        self,
        perceived: Dict[str, Any],
        reflection: Dict[str, Any],
        intention: Dict[str, Any],
        system_callback_fn: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Stage 4: Act - Dispatch action, log out-of-band step, and report outcome."""
        target_action = intention["target_action"]
        stimulus = perceived["raw_stimulus"]
        step_id = None
        action_status = "completed"

        if target_action == "deep_deliberation_wal" and system_callback_fn:
            step = system_callback_fn(
                phase=StepPhase.DELIBERATION,
                title=f"Analytical Reflection: {stimulus[:40]}...",
                thought=f"Mind4Action Reflected: {reflection['insights']}. Raw: {stimulus}",
                observation=f"Intention: {intention['rationale']}",
                is_milestone=False
            )
            step_id = step.step_id if hasattr(step, "step_id") else None
            action_status = "logged_to_leveldb_wal"

        elif target_action == "breakdown_and_consolidate" and system_callback_fn:
            step = system_callback_fn(
                phase=StepPhase.REVISION,
                title="Fatigue Mitigation & Memory Consolidation",
                thought="Detected elevated cognitive load. Shielding active prompt and consolidating memory state.",
                observation="Memory consolidated. Restoring flow state.",
                is_milestone=True
            )
            step_id = step.step_id if hasattr(step, "step_id") else None
            action_status = "consolidated_memory"

        return {
            "action_executed": target_action,
            "status": action_status,
            "step_id": step_id,
            "active_prompt_shielded": True,
            "timestamp": time.time()
        }

    def run_cycle(
        self,
        stimulus: str,
        scann_results: Optional[List[Dict[str, Any]]] = None,
        firewall_inspection: Optional[Dict[str, Any]] = None,
        system_step_fn: Optional[Any] = None,
    ) -> Mind4ActionTurn:
        """Execute a complete Perceive -> Reflect -> Intend -> Act cognitive cycle."""
        self._turn_counter += 1
        perceived = self.perceive(stimulus)
        reflected = self.reflect(perceived, scann_results=scann_results)
        
        inspection = firewall_inspection or {
            "blocked": False,
            "reason": None,
            "allocated_budget": 700,
            "shielded_tokens": 0
        }
        
        intended = self.intend(perceived, reflected, inspection)
        action_result = self.act(perceived, reflected, intended, system_callback_fn=system_step_fn)

        turn = Mind4ActionTurn(
            stimulus=stimulus,
            reflection=reflected,
            intention=intended,
            action_result=action_result,
            cognitive_state=self.state.model_copy(),
            firewall_interventions=1 if inspection.get("blocked") else 0
        )
        self.history.append(turn)
        return turn

    def get_latest_state(self) -> CognitiveState:
        return self.state

    def get_recent_turns(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [t.model_dump() for t in self.history[-limit:]]
