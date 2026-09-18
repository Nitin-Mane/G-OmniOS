"""G-OmniOS: Universal AI Operating System & Cognitive Memory Platform.

A zero-token-bloat cognitive memory allocation, Mind4Action reasoning engine,
and multi-agent operating system fusing Google open-source technologies:
- Google Always-On Memory Agent (Decoupled ingestion & background consolidation)
- Google Research ReasoningBank (Strategy & progress step abstraction)
- Google Diff-Match-Patch (Context revision & delta computation)
- Google LevelDB-style Embedded Step Ledger (Append-only WAL)
- Google ScaNN-inspired Vector Memory (Local semantic recall)
- Google SentencePiece Token Budget Governor (Tiered allocation)
- Mind4Action Engine (Perceive -> Reflect -> Intend -> Act)
- Multi-Disciplinary Agent Teams (Manager, HR, Fullstack, Catalog, Marketing, DevOps)
"""

__version__ = "1.0.0"

from omni_memory.engine import GOmniOSSystem, OmniMemorySystem
from omni_memory.models.step import Step, StepPhase
from omni_memory.models.cognitive_profile import (
    AbilityTrack,
    CognitivePattern,
    PsychologicalBehavior,
    CognitiveState,
    PersonaSkill,
)

__all__ = [
    "GOmniOSSystem",
    "OmniMemorySystem",
    "Step",
    "StepPhase",
    "AbilityTrack",
    "CognitivePattern",
    "PsychologicalBehavior",
    "CognitiveState",
    "PersonaSkill",
]
