"""Google Always-On Memory Agent for OmniMemory.

Implements the multi-agent decoupled memory architecture:
1. Listens out-of-band to progress steps and thought traces.
2. Performs Context Revision via Google Diff-Match-Patch and ReasoningBank distillation.
3. Saves canonical memory state into LevelDB, ScaNN, and tiered allocations.
4. Exposes surgical on-demand retrieval tools for the primary task agent.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple
from omni_memory.models.step import ProgressStep, StepPhase
from omni_memory.models.memory_tier import TierType, MemorySlot
from omni_memory.models.context_revision import ContextRevision
from omni_memory.core.diff_patch_engine import GoogleDiffMatchPatch
from omni_memory.core.allocator import MemoryAllocator, estimate_sentencepiece_tokens
from omni_memory.core.scann_vector_engine import ScaNNVectorEngine
from omni_memory.core.leveldb_store import LevelDBStepLedger


class MemoryAgent:
    """The dedicated Memory Agent that observes, revises, and persists context."""

    def __init__(
        self,
        allocator: MemoryAllocator,
        scann_engine: ScaNNVectorEngine,
        ledger: LevelDBStepLedger,
        diff_engine: Optional[GoogleDiffMatchPatch] = None,
        revision_step_threshold: int = 3,  # Revise context every N steps
    ):
        self.allocator = allocator
        self.scann_engine = scann_engine
        self.ledger = ledger
        self.diff_engine = diff_engine or GoogleDiffMatchPatch()
        self.revision_threshold = revision_step_threshold
        
        # Internal state
        self._unrevised_steps: List[ProgressStep] = []
        self._current_canonical_context: str = "Initial task context: Objective started."
        self._active_goals: List[str] = []
        self._resolved_goals: List[str] = []
        self._key_facts: Dict[str, str] = {}
        self._revisions_history: List[ContextRevision] = []
        
        # Listeners for revision events
        self._revision_listeners: List[Any] = []

    def register_revision_listener(self, callback: Any) -> None:
        self._revision_listeners.append(callback)

    def on_step_received(self, step: ProgressStep) -> None:
        """Callback invoked out-of-band by StepTracker for each progress step."""
        self._unrevised_steps.append(step)
        
        # Index step into ScaNN vector memory for instant on-demand retrieval
        step_text = f"Step {step.sequence_num} ({step.phase.value}): {step.title}"
        if step.thought_trace and step.thought_trace.content:
            step_text += f" | Thought: {step.thought_trace.content}"
        if step.observation:
            step_text += f" | Observation: {step.observation}"
        
        step_slot = MemorySlot(
            slot_id=f"step_{step.session_id}_{step.sequence_num}",
            tier=TierType.EPISODIC if step.is_milestone else TierType.WORKING,
            key=f"steps:{step.session_id}:{step.sequence_num:08d}",
            content=step_text,
            token_cost=step.token_weight,
            importance=1.5 if step.is_milestone else 1.0,
        )
        self.scann_engine.add_slot(step_slot)
        
        # If this step is a designated milestone or we hit our batch threshold, revise
        if step.is_milestone or len(self._unrevised_steps) >= self.revision_threshold:
            self.revise_and_consolidate()

    def revise_and_consolidate(self) -> Optional[ContextRevision]:
        """Perform context revision: distill unrevised steps into clean state updates."""
        if not self._unrevised_steps:
            return self._revisions_history[-1] if self._revisions_history else None

        step_start = self._unrevised_steps[0].sequence_num
        step_end = self._unrevised_steps[-1].sequence_num
        
        # Calculate raw tokens consumed across these steps
        raw_tokens = sum(s.token_weight for s in self._unrevised_steps)

        # Distill knowledge and facts from steps (Google ReasoningBank pattern)
        new_facts: List[str] = []
        for step in self._unrevised_steps:
            # Extract key decisions and insights concisely for canonical prompt state
            insight = f"Step {step.sequence_num} ({step.phase.value}): {step.title}"
            if step.observation:
                insight += f" -> Outcome: {step.observation[:80]}"
            new_facts.append(insight)
                
            # If step marks a goal resolution or is a milestone
            if step.is_milestone and step.title not in self._resolved_goals:
                self._resolved_goals.append(step.title)
            if step.tags and "resolved" in step.tags:
                if step.title not in self._resolved_goals:
                    self._resolved_goals.append(step.title)
            elif step.tags and "goal" in step.tags:
                if step.title not in self._active_goals:
                    self._active_goals.append(step.title)

        # Build revised context synthesis
        previous_text = self._current_canonical_context
        
        # Format clean, consolidated memory frame
        revised_lines = [
            f"=== CONSOLIDATED MEMORY STATE (Steps 1-{step_end}) ===",
            f"Active Objective / Goals: {', '.join(self._active_goals) or 'Executing task pipeline'}",
            f"Resolved Milestones: {', '.join(self._resolved_goals) or 'None yet'}",
            "Key State Variables & Findings:",
        ]
        for fact in new_facts[-5:]:  # Keep recent salient items
            revised_lines.append(f"  • {fact}")
            
        revised_text = "\n".join(revised_lines)
        revised_tokens = estimate_sentencepiece_tokens(revised_text)

        # Generate Google Diff-Match-Patch revision
        revision = self.diff_engine.generate_revision(
            session_id=self._unrevised_steps[0].session_id,
            step_start=step_start,
            step_end=step_end,
            previous_context=previous_text,
            revised_context=revised_text,
            raw_tokens_consumed=raw_tokens,
            revised_tokens=revised_tokens,
            active_goals=list(self._active_goals),
            resolved_goals=list(self._resolved_goals),
        )

        # Update canonical context state
        self._current_canonical_context = revised_text
        self._revisions_history.append(revision)

        # 1. Update Working Memory slot in Allocator (budget-controlled)
        self.allocator.allocate(
            key="canonical_context",
            content=revised_text,
            tier=TierType.WORKING,
            importance=2.0,  # High importance
            metadata={"revision_id": revision.revision_id, "step_end": step_end},
        )

        # 2. Consolidate into Episodic Memory (ReasoningBank milestone)
        episodic_content = (
            f"Milestone [Steps {step_start}-{step_end}]: "
            + "; ".join(s.title for s in self._unrevised_steps)
        )
        episodic_slot = self.allocator.allocate(
            key=f"milestone_{step_end}",
            content=episodic_content,
            tier=TierType.EPISODIC,
            importance=1.5,
            metadata={"step_range": [step_start, step_end]},
        )

        # 3. Index key facts into ScaNN Vector Semantic Memory
        for fact in new_facts:
            sem_slot = MemorySlot(
                slot_id=f"sem_{step_end}_{int(time.time() * 1000) % 100000}",
                tier=TierType.SEMANTIC,
                key=f"fact_step_{step_end}",
                content=fact,
                token_cost=estimate_sentencepiece_tokens(fact),
                created_at=time.time(),
                last_accessed=time.time(),
                importance=1.0,
            )
            self.scann_engine.add_slot(sem_slot)

        # Clear unrevised step buffer
        self._unrevised_steps.clear()

        # Notify listeners
        for listener in self._revision_listeners:
            try:
                listener(revision)
            except Exception as e:
                print(f"[MemoryAgent] Error notifying revision listener: {e}")

        return revision

    def query_memory(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Surgical on-demand retrieval for the Task LLM without prompt bloat."""
        results = self.scann_engine.search(query, top_k=top_k)
        return [
            {
                "slot_id": slot.slot_id,
                "tier": slot.tier.value,
                "content": slot.content,
                "relevance": round(score, 3),
                "token_cost": slot.token_cost,
            }
            for slot, score in results
        ]

    def get_canonical_context(self) -> str:
        """Return the current distilled canonical context."""
        return self._current_canonical_context

    def get_revision_history(self) -> List[ContextRevision]:
        """Return all context revisions generated."""
        return self._revisions_history

    def reset(self, new_context: str = "Initial task context: Objective started.") -> None:
        """Reset agent internal memory state for a new session."""
        self._unrevised_steps.clear()
        self._current_canonical_context = new_context
        self._active_goals.clear()
        self._resolved_goals.clear()
        self._key_facts.clear()
        self._revisions_history.clear()
