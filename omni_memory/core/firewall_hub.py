"""Cognitive & Memory Firewall Hub for G-OmniOS.

Provides out-of-band monitoring, filtering, and persona skill scheduling
across Technical, Social, and Mental ability tracks. Prevents cognitive
overload, prompt bloat, and unauthorized psychological data leakage.
"""

from __future__ import annotations
import re
import time
from typing import Any, Dict, List, Optional
from omni_memory.models.cognitive_profile import (
    AbilityTrack,
    CognitivePattern,
    PsychologicalBehavior,
    CognitiveState,
    PersonaSkill,
)


# Default Comprehensive Catalog of Persona Skills across Ability Tracks
DEFAULT_PERSONA_CATALOG: Dict[str, PersonaSkill] = {
    # 1. Technical Ability Track
    "tech_distributed_consensus": PersonaSkill(
        skill_id="tech_distributed_consensus",
        title="Raft Consensus & Distributed State Machine",
        track=AbilityTrack.TECHNICAL,
        level="advanced",
        description="Leader election, heartbeat replication, quorum safety, and log compaction with strict out-of-band step tracking.",
        system_prompt="Build a distributed consensus state machine with Raft election and quorum replication.",
        prompt_budget=600,
        prerequisites=["network_fundamentals", "state_machines"],
        recommended_phases=["deliberation", "hypothesis", "planning", "code_gen", "execution", "verification"],
        tags=["consensus", "raft", "distributed-systems", "leveldb"]
    ),
    "tech_quant_risk_parity": PersonaSkill(
        skill_id="tech_quant_risk_parity",
        title="Algorithmic Trading & Risk Parity Strategy",
        track=AbilityTrack.TECHNICAL,
        level="master",
        description="Covariance matrix deconstruction, volatility budgeting, dynamic leverage scaling, and ScaNN rule indexing.",
        system_prompt="Synthesize an algorithmic trading strategy with risk parity constraints and dynamic leverage scaling.",
        prompt_budget=800,
        prerequisites=["linear_algebra", "portfolio_theory"],
        recommended_phases=["deliberation", "hypothesis", "planning", "code_gen", "execution", "verification"],
        tags=["quant", "risk-parity", "slsqp", "scann"]
    ),
    "tech_ast_refactor": PersonaSkill(
        skill_id="tech_ast_refactor",
        title="Autonomous Code Refactoring & Invariant Synthesis",
        track=AbilityTrack.TECHNICAL,
        level="intermediate",
        description="Zero-regression codebase modernization, invariant extraction, AST transformation, and Diff-Match-Patch delta auditing.",
        system_prompt="Refactor monolithic agent service into decoupled out-of-band memory micro-architecture with verified invariants.",
        prompt_budget=700,
        prerequisites=["ast_parsing", "unit_testing"],
        recommended_phases=["deliberation", "planning", "code_gen", "verification"],
        tags=["refactoring", "ast", "diff-match-patch", "invariants"]
    ),

    # 2. Social Ability Track
    "social_collaborative_synthesis": PersonaSkill(
        skill_id="social_collaborative_synthesis",
        title="Multi-Stakeholder Architectural Consensus",
        track=AbilityTrack.SOCIAL,
        level="advanced",
        description="Synthesizes divergent engineering viewpoints, reconciles technical trade-offs, and documents cross-team alignment.",
        system_prompt="Mediate architectural trade-offs between speed, durability, and cost. Build consensus across stakeholder perspectives.",
        prompt_budget=750,
        prerequisites=["communication", "systems_design"],
        recommended_phases=["deliberation", "planning", "verification"],
        tags=["collaboration", "consensus", "architecture", "stakeholders"]
    ),
    "social_empathic_code_review": PersonaSkill(
        skill_id="social_empathic_code_review",
        title="Psychologically Safe & Constructive Code Review",
        track=AbilityTrack.SOCIAL,
        level="intermediate",
        description="Provides precise, uplifting, and actionable code feedback that enhances team psychological safety and code quality.",
        system_prompt="Review implementation with rigorous technical standards while providing psychologically safe, educational commentary.",
        prompt_budget=650,
        prerequisites=["code_review", "psychological_safety"],
        recommended_phases=["deliberation", "verification"],
        tags=["code-review", "empathy", "mentorship", "safety"]
    ),
    "social_executive_briefing": PersonaSkill(
        skill_id="social_executive_briefing",
        title="Executive Strategic Decision Briefing",
        track=AbilityTrack.SOCIAL,
        level="foundational",
        description="Distills complex algorithmic invariants and engineering progress into clear, high-impact executive summaries.",
        system_prompt="Translate dense technical telemetry, token savings economics, and milestone progress into an executive briefing.",
        prompt_budget=600,
        prerequisites=["communication"],
        recommended_phases=["planning", "verification"],
        tags=["executive", "presentation", "decision-making"]
    ),

    # 3. Mental Ability Track
    "mental_cognitive_resilience": PersonaSkill(
        skill_id="mental_cognitive_resilience",
        title="High-Pressure Root Cause Debugging & Failure Recovery",
        track=AbilityTrack.MENTAL,
        level="advanced",
        description="Maintains calm, structured reasoning under critical production outages and cascading failure scenarios.",
        system_prompt="Execute systematic root-cause analysis on active system failure. Maintain zero panic, verify invariants step-by-step.",
        prompt_budget=700,
        prerequisites=["debugging", "incident_management"],
        recommended_phases=["deliberation", "hypothesis", "execution", "verification"],
        tags=["resilience", "debugging", "incident", "stress-recovery"]
    ),
    "mental_meta_cognition": PersonaSkill(
        skill_id="mental_meta_cognition",
        title="Meta-Cognitive Bias Audit & Invariant Reflection",
        track=AbilityTrack.MENTAL,
        level="master",
        description="Continuously audits the model's own reasoning assumptions, identifying blind spots, confirmation bias, and false premises.",
        system_prompt="Conduct meta-cognitive review of recent reasoning iterations. Question assumptions and verify boundary cases.",
        prompt_budget=650,
        prerequisites=["critical_thinking", "formal_logic"],
        recommended_phases=["deliberation", "verification", "revision"],
        tags=["meta-cognition", "bias-audit", "critical-thinking"]
    ),
    "mental_focus_stamina": PersonaSkill(
        skill_id="mental_focus_stamina",
        title="Deep-Work Focus Gating & Anti-Distraction",
        track=AbilityTrack.MENTAL,
        level="foundational",
        description="Shields working memory from context thrashing, keeping the agent strictly on core objectives for extended task runs.",
        system_prompt="Execute deep-work focus gating. Filter non-essential tasks and maintain continuous progress on primary objective.",
        prompt_budget=550,
        prerequisites=["time_management"],
        recommended_phases=["deliberation", "planning", "execution"],
        tags=["focus", "flow", "stamina", "anti-bloat"]
    ),
}


class MemoryFirewallHub:
    """Active firewall shielding user cognitive state and monitoring token economics."""

    def __init__(self):
        self.catalog: Dict[str, PersonaSkill] = dict(DEFAULT_PERSONA_CATALOG)
        self.active_skill: Optional[PersonaSkill] = None
        self.scheduled_queue: List[PersonaSkill] = []
        
        # Firewall metrics
        self.total_inspections = 0
        self.total_blocked = 0
        self.shielded_tokens = 0
        self.rules_triggered: Dict[str, int] = {
            "cognitive_overload": 0,
            "psychological_leakage": 0,
            "repetitive_loop": 0,
            "prompt_bloat": 0,
        }

    def inspect_prompt(self, text: str, state: CognitiveState) -> Dict[str, Any]:
        """Inspect prompt for cognitive overload, psychological leaks, or bloat."""
        self.total_inspections += 1
        raw_tokens = max(1, len(text.split()))

        # Rule 1: Cognitive Overload Guard
        # If user/agent cognitive load is high (>0.80) and prompt is excessively verbose
        if state.cognitive_load_index > 0.80 and raw_tokens > 400:
            self.total_blocked += 1
            self.rules_triggered["cognitive_overload"] += 1
            shielded = raw_tokens - 200
            self.shielded_tokens += shielded
            return {
                "blocked": True,
                "reason": "Cognitive Overload Guard: Prompt exceeds mental bandwidth threshold.",
                "allocated_budget": 400,
                "shielded_tokens": shielded,
                "rule": "cognitive_overload"
            }

        # Rule 2: Repetitive Thought Loop
        words = text.lower().split()
        if len(words) > 30 and len(set(words)) / len(words) < 0.35:
            self.total_blocked += 1
            self.rules_triggered["repetitive_loop"] += 1
            return {
                "blocked": True,
                "reason": "Repetitive Loop Detected: Agent is cycling on redundant concepts.",
                "allocated_budget": 500,
                "shielded_tokens": raw_tokens,
                "rule": "repetitive_loop"
            }

        # Rule 3: Psychological Vulnerability Leakage
        # Catches raw sensitive personal expressions that should stay private in LevelDB WAL
        sensitive_patterns = [
            r"\b(i am having a panic attack|i hate myself|severely depressed|private password|api key)\b"
        ]
        for pat in sensitive_patterns:
            if re.search(pat, text, re.IGNORECASE):
                self.total_blocked += 1
                self.rules_triggered["psychological_leakage"] += 1
                return {
                    "blocked": True,
                    "reason": "Psychological Safety Guard: Sensitive personal or secret data detected.",
                    "allocated_budget": 300,
                    "shielded_tokens": raw_tokens,
                    "rule": "psychological_leakage"
                }

        # Rule 4: Standard Prompt Bloat Guard
        allocated_budget = 700
        if raw_tokens > allocated_budget:
            shielded = raw_tokens - allocated_budget
            self.shielded_tokens += shielded
            self.rules_triggered["prompt_bloat"] += 1
            return {
                "blocked": False,
                "reason": f"Prompt Bloat Shield: {shielded} raw tokens diverted out-of-band to LevelDB WAL.",
                "allocated_budget": allocated_budget,
                "shielded_tokens": shielded,
                "rule": "prompt_bloat"
            }

        return {
            "blocked": False,
            "reason": "Clean Context: Within all cognitive safety and token budget invariants.",
            "allocated_budget": allocated_budget,
            "shielded_tokens": 0,
            "rule": "pass"
        }

    def schedule_skill(self, skill_id: str) -> Optional[PersonaSkill]:
        """Schedule and activate a persona skill from the catalog."""
        skill = self.catalog.get(skill_id)
        if skill:
            self.active_skill = skill
            self.scheduled_queue.append(skill)
            return skill
        return None

    def get_catalog_by_track(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group all persona skills by universal ability track."""
        grouped: Dict[str, List[Dict[str, Any]]] = {
            AbilityTrack.TECHNICAL.value: [],
            AbilityTrack.SOCIAL.value: [],
            AbilityTrack.MENTAL.value: [],
        }
        for skill in self.catalog.values():
            grouped[skill.track.value].append(skill.model_dump())
        return grouped

    def get_catalog(self) -> List[PersonaSkill]:
        """Return full list of persona skills in catalog."""
        return list(self.catalog.values())

    def get_firewall_status(self) -> Dict[str, Any]:
        """Return firewall statistics and active interventions."""
        return {
            "total_inspections": self.total_inspections,
            "total_interventions": self.total_blocked,
            "shielded_tokens": self.shielded_tokens,
            "rules_triggered": self.rules_triggered,
            "active_skill": self.active_skill.model_dump() if self.active_skill else None,
            "scheduled_count": len(self.scheduled_queue),
            "safety_health_score": round(max(0.0, 1.0 - (self.total_blocked / max(1, self.total_inspections))), 2)
        }

    def get_status(self) -> Dict[str, Any]:
        """Alias for get_firewall_status with config details."""
        st = self.get_firewall_status()
        st["rules"] = ["cognitive_overload", "psychological_leakage", "repetitive_loop", "prompt_bloat"]
        st["max_prompt_tokens"] = 700
        st["cognitive_load_threshold"] = 0.80
        return st
