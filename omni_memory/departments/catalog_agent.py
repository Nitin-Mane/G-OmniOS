"""Product Catalog Agent for G-OmniOS.

Curates persona skills, templates, and capability blueprints across
the Technical, Social, and Mental ability tracks.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from omni_memory.models.cognitive_profile import AbilityTrack, CognitiveState, PersonaSkill
from omni_memory.core.firewall_hub import DEFAULT_PERSONA_CATALOG


class CatalogAgent:
    """Manages the persona skills catalog and capability recommendations."""

    def __init__(self):
        self.role = "Product Catalog & Capability Architect"
        self.catalog = dict(DEFAULT_PERSONA_CATALOG)

    def list_all_skills(self) -> Dict[str, Any]:
        """List all catalog skills grouped by universal ability track."""
        grouped: Dict[str, List[Dict[str, Any]]] = {
            AbilityTrack.TECHNICAL.value: [],
            AbilityTrack.SOCIAL.value: [],
            AbilityTrack.MENTAL.value: [],
        }
        for s in self.catalog.values():
            grouped[s.track.value].append(s.model_dump())
        return {
            "agent": "CatalogAgent",
            "role": self.role,
            "total_skills": len(self.catalog),
            "tracks": grouped,
            "timestamp": time.time(),
        }

    def recommend_skills_for_state(self, state: CognitiveState) -> List[Dict[str, Any]]:
        """Recommend optimal persona skills tailored to current cognitive state."""
        recommendations: List[Dict[str, Any]] = []

        if state.cognitive_load_index > 0.70:
            # Recommend Mental resilience or Social briefing to de-escalate cognitive load
            for s_id in ["mental_focus_stamina", "social_executive_briefing"]:
                if s_id in self.catalog:
                    recommendations.append(self.catalog[s_id].model_dump())
        elif state.flow_score > 0.80:
            # Deep flow: recommend advanced Technical skills
            for s_id in ["tech_quant_risk_parity", "tech_distributed_consensus"]:
                if s_id in self.catalog:
                    recommendations.append(self.catalog[s_id].model_dump())
        else:
            # Foundational skills
            for s in self.catalog.values():
                if s.level in ("foundational", "intermediate"):
                    recommendations.append(s.model_dump())
                    if len(recommendations) >= 3:
                        break

        return recommendations
