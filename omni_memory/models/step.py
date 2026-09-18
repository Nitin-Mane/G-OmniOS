"""Step and thought models for Google OmniMemory.

Implements structured tracking schemas aligned with Google Research ReasoningBank
and Google Protobuf/FlatBuffers serialization standards.
"""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StepPhase(str, Enum):
    """Execution and deliberation phases of an LLM agent."""
    DELIBERATION = "deliberation"      # Model internal reasoning / chain-of-thought
    HYPOTHESIS = "hypothesis"          # Proposed solution path or assumption
    PLANNING = "planning"              # Structured plan generation
    CODE_GEN = "code_gen"              # Code / text artifact writing
    EXECUTION = "execution"            # Tool execution or command execution
    VERIFICATION = "verification"      # Self-correction, linting, testing
    REVISION = "revision"              # Context revision by the Memory Agent


class ThoughtTrace(BaseModel):
    """Detailed thought trace captured out-of-band without expanding prompt tokens."""
    trace_id: str = Field(default_factory=lambda: f"th_{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(default_factory=time.time)
    content: str
    rationale: Optional[str] = None
    confidence: float = 1.0
    token_count: int = 0


class ProgressStep(BaseModel):
    """Atomic step in a multi-step reasoning or generation task.
    
    Saved directly to Google LevelDB WAL without being appended to the
    primary LLM's active prompt.
    """
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:10]}")
    session_id: str
    sequence_num: int
    timestamp: float = Field(default_factory=time.time)
    phase: StepPhase
    title: str
    
    # Verbose payloads captured OUT-OF-BAND:
    thought_trace: Optional[ThoughtTrace] = None
    action_type: Optional[str] = None
    action_payload: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    
    # State tracking & token economics:
    token_weight: int = 0              # Raw tokens this step would have consumed in-prompt
    is_milestone: bool = False         # Strategy milestone for ReasoningBank
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_summary_dict(self) -> Dict[str, Any]:
        """Summary with out-of-band payloads for web console and memory inspection."""
        return {
            "step_id": self.step_id,
            "session_id": self.session_id,
            "seq": self.sequence_num,
            "phase": self.phase.value,
            "title": self.title,
            "tokens": self.token_weight,
            "is_milestone": self.is_milestone,
            "thought": self.thought_trace.content if self.thought_trace else "",
            "rationale": self.thought_trace.rationale if self.thought_trace else "",
            "observation": self.observation or "",
            "wal_key": f"steps:{self.session_id}:{self.sequence_num:08d}",
            "timestamp": self.timestamp,
        }
