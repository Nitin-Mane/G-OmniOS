"""Out-of-band Step Tracker for OmniMemory.

Hooks into the LLM's deliberation, code generation, and tool actions,
recording all intermediate traces directly to Google LevelDB without
appending them to the prompt context.
"""

from __future__ import annotations
import time
from typing import Any, Callable, Dict, List, Optional
from omni_memory.models.step import ProgressStep, StepPhase, ThoughtTrace
from omni_memory.core.allocator import MemoryAllocator, estimate_sentencepiece_tokens
from omni_memory.core.leveldb_store import LevelDBStepLedger


class StepTracker:
    """Tracks and records execution steps out-of-band."""

    def __init__(
        self,
        ledger: LevelDBStepLedger,
        allocator: MemoryAllocator,
        session_id: str = "default_session",
    ):
        self.ledger = ledger
        self.allocator = allocator
        self.session_id = session_id
        self._sequence_counter: int = 0
        
        # Observers (e.g. Memory Agent, Web Console event bus)
        self._listeners: List[Callable[[ProgressStep], None]] = []

    def add_listener(self, callback: Callable[[ProgressStep], None]) -> None:
        """Register a callback that receives every step event out-of-band."""
        self._listeners.append(callback)

    def track_step(
        self,
        phase: StepPhase,
        title: str,
        thought_content: Optional[str] = None,
        thought_rationale: Optional[str] = None,
        action_type: Optional[str] = None,
        action_payload: Optional[Dict[str, Any]] = None,
        observation: Optional[str] = None,
        is_milestone: bool = False,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProgressStep:
        """Record an LLM step out-of-band.
        
        Calculates token weight, saves to LevelDB, and notifies the Memory Agent.
        The primary prompt context remains untouched.
        """
        self._sequence_counter += 1
        
        # Construct thought trace if present
        thought_trace = None
        thought_tokens = 0
        if thought_content:
            thought_tokens = estimate_sentencepiece_tokens(thought_content)
            thought_trace = ThoughtTrace(
                content=thought_content,
                rationale=thought_rationale,
                token_count=thought_tokens,
            )
            
        action_tokens = estimate_sentencepiece_tokens(str(action_payload or ""))
        obs_tokens = estimate_sentencepiece_tokens(str(observation or ""))
        total_step_tokens = thought_tokens + action_tokens + obs_tokens + estimate_sentencepiece_tokens(title)

        step = ProgressStep(
            session_id=self.session_id,
            sequence_num=self._sequence_counter,
            timestamp=time.time(),
            phase=phase,
            title=title,
            thought_trace=thought_trace,
            action_type=action_type,
            action_payload=action_payload,
            observation=observation,
            token_weight=total_step_tokens,
            is_milestone=is_milestone,
            tags=tags or [],
            metadata=metadata or {},
        )

        # 1. Persist to LevelDB out-of-band
        self.ledger.append_step(step)
        
        # 2. Record token savings in allocator
        self.allocator.record_raw_step_overhead(total_step_tokens)

        # 3. Notify asynchronous listeners (Memory Agent)
        for listener in self._listeners:
            try:
                listener(step)
            except Exception as e:
                # Observers must not crash primary execution
                print(f"[StepTracker] Listener notification error: {e}")

        return step

    def get_history(self) -> List[ProgressStep]:
        """Fetch all recorded steps from LevelDB ledger."""
        return self.ledger.get_steps_for_session(self.session_id)

    def get_step_count(self) -> int:
        return self._sequence_counter

    def reset(self, new_session_id: str) -> None:
        """Reset sequence counter and update session ID."""
        self.session_id = new_session_id
        self._sequence_counter = 0
