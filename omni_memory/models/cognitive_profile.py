"""Cognitive, psychological, and persona skill models for G-OmniOS.

Defines schemas for Mind4Action activity cycles, psychological behaviors,
cognitive patterns, and multi-tier ability tracks (Technical, Social, Mental).
"""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AbilityTrack(str, Enum):
    """Universal ability tracks representing human and agent capability domains."""
    TECHNICAL = "technical"   # Architecture, quantitative reasoning, code synthesis, algorithms
    SOCIAL = "social"         # Collaborative synthesis, empathy, consensus building, communication
    MENTAL = "mental"         # Cognitive resilience, meta-cognition, focus stamina, structured thinking


class CognitivePattern(str, Enum):
    """Primary thinking and cognitive processing styles."""
    ANALYTICAL = "analytical"       # Deep decomposition, step-by-step invariant validation
    INTUITIVE = "intuitive"         # Heuristic jumping, holistic pattern matching
    SYSTEMATIC = "systematic"       # Methodical checklists, deterministic pipeline following
    DIVERGENT = "divergent"         # Creative exploration, alternative hypothesis generation
    CONVERGENT = "convergent"       # Focused synthesis, distillation to single optimal decision


class PsychologicalBehavior(str, Enum):
    """Psychological operational states observed during problem-solving."""
    FLOW = "flow"                   # Optimal performance, low friction, steady cadence
    FATIGUE = "fatigue"             # Degrading focus, repetition, high token cost per insight
    HYPERFOCUS = "hyperfocus"       # Deep single-track focus, risk of missing broader constraints
    EXPLORATION = "exploration"     # Broad scanning, high curiosity, seeking external references
    DELIBERATE = "deliberate"       # High caution, deep reflection, risk mitigation focus
    OVERLOAD = "overload"           # Rapid context switching, prompt bloat, cognitive exhaustion


class Mind4ActionPhase(str, Enum):
    """Four-stage cognitive activity cycle."""
    PERCEIVE = "perceive"   # Absorbing raw input stimulus and external events
    REFLECT = "reflect"     # Psychological and cognitive evaluation, ScaNN memory association
    INTEND = "intend"       # Firewall rule filtering, bounded goal formulation
    ACT = "act"             # Persona skill execution or out-of-band step recording


class CognitiveState(BaseModel):
    """Live assessment of user/agent mental state and cognitive load."""
    cognitive_load_index: float = Field(default=0.25, ge=0.0, le=1.0)  # 0.0 (fresh) to 1.0 (exhausted)
    flow_score: float = Field(default=0.85, ge=0.0, le=1.0)           # 0.0 (blocked) to 1.0 (deep flow)
    deliberation_depth: float = Field(default=0.60, ge=0.0, le=1.0)    # Intensity of internal thought
    stress_indicator: float = Field(default=0.15, ge=0.0, le=1.0)      # Risk of cognitive breakdown
    primary_pattern: CognitivePattern = CognitivePattern.ANALYTICAL
    active_behavior: PsychologicalBehavior = PsychologicalBehavior.FLOW
    last_updated: float = Field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cognitive_load_index": round(self.cognitive_load_index, 2),
            "flow_score": round(self.flow_score, 2),
            "deliberation_depth": round(self.deliberation_depth, 2),
            "stress_indicator": round(self.stress_indicator, 2),
            "primary_pattern": self.primary_pattern.value,
            "active_behavior": self.active_behavior.value,
            "last_updated": self.last_updated,
        }


class PersonaSkill(BaseModel):
    """A modular memory-building persona capability tailored to user ability."""
    skill_id: str
    title: str
    track: AbilityTrack
    level: str = "intermediate"  # foundational, intermediate, advanced, master
    description: str
    system_prompt: str
    prompt_budget: int = 700
    prerequisites: List[str] = Field(default_factory=list)
    recommended_phases: List[str] = Field(default_factory=lambda: ["deliberation", "planning", "execution", "verification"])
    tags: List[str] = Field(default_factory=list)


class Mind4ActionTurn(BaseModel):
    """Record of a complete Mind4Action cognitive turn."""
    turn_id: str = Field(default_factory=lambda: f"m4a_{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(default_factory=time.time)
    stimulus: str
    reflection: Dict[str, Any]
    intention: Dict[str, Any]
    action_result: Dict[str, Any]
    cognitive_state: CognitiveState
    firewall_interventions: int = 0
