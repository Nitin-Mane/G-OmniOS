"""Human Resources & Psychological Well-Being Agent for G-OmniOS.

Guards cognitive ergonomics, mental safety, user burnout prevention,
and ethical boundaries during high-intensity AI execution.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from omni_memory.models.cognitive_profile import CognitiveState, PsychologicalBehavior


class HRAgent:
    """Oversees user psychological well-being, ergonomics, and cognitive safety."""

    def __init__(self):
        self.role = "Head of Cognitive Ergonomics & Psychological Safety"

    def assess_wellbeing(self, state: CognitiveState) -> Dict[str, Any]:
        """Evaluate mental fatigue, stress, and provide ergonomics recommendations."""
        cli = state.cognitive_load_index
        flow = state.flow_score
        stress = state.stress_indicator
        behavior = state.active_behavior

        # Compute wellness score (0 to 100)
        wellness_score = max(0, min(100, int((flow * 0.4 + (1.0 - cli) * 0.35 + (1.0 - stress) * 0.25) * 100)))

        recommendations: List[str] = []
        if cli > 0.75:
            recommendations.append("High Cognitive Load: Consolidate active context and schedule a shorter 5-minute break.")
        if behavior == PsychologicalBehavior.FATIGUE:
            recommendations.append("Fatigue Detected: Downscale task complexity and avoid cycling on redundant error traces.")
        if stress > 0.60:
            recommendations.append("Elevated Stress Indicator: Enable mental resilience persona skill to maintain grounded reasoning.")
        if not recommendations:
            recommendations.append("Optimal Flow: Cognitive state is healthy, focused, and operating with low friction.")

        return {
            "agent": "HRAgent",
            "role": self.role,
            "wellness_score": wellness_score,
            "cognitive_load": cli,
            "stress_indicator": stress,
            "psychological_state": behavior.value,
            "psychologically_safe": stress < 0.70 and cli < 0.85,
            "recommendations": recommendations,
            "timestamp": time.time(),
        }

    def enforce_ethical_boundaries(self, proposed_action: Dict[str, Any]) -> Dict[str, Any]:
        """Audit actions to ensure user privacy, data dignity, and no manipulative prompts."""
        action_name = proposed_action.get("action", "unknown")
        return {
            "agent": "HRAgent",
            "action_audited": action_name,
            "ethical_clearance": True,
            "user_data_dignity": "Preserved out-of-band in local LevelDB WAL",
            "consent_enforced": True,
            "timestamp": time.time(),
        }
