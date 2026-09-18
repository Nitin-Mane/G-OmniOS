"""Primary Task LLM Agent with Decoupled Memory Hook for OmniMemory.

Executes complex multi-step reasoning and writing tasks with a strictly
bounded prompt context. All intermediate thought traces and execution steps
are routed out-of-band to the Memory Agent.
"""

from __future__ import annotations
import time
from typing import Any, Callable, Dict, List, Optional
from omni_memory.models.step import ProgressStep, StepPhase
from omni_memory.core.tracker import StepTracker
from omni_memory.core.allocator import MemoryAllocator, estimate_sentencepiece_tokens
from omni_memory.agents.memory_agent import MemoryAgent


class TaskAgent:
    """Primary Task Agent that runs with zero prompt bloat."""

    def __init__(
        self,
        name: str,
        tracker: StepTracker,
        allocator: MemoryAllocator,
        memory_agent: MemoryAgent,
        llm_fn: Optional[Callable[[str, str], str]] = None,
    ):
        self.name = name
        self.tracker = tracker
        self.allocator = allocator
        self.memory_agent = memory_agent
        self.llm_fn = llm_fn
        
        # Initial task prompt (fixed cost)
        self.initial_prompt: str = ""
        self.system_instructions: str = (
            "You are an expert autonomous problem-solving agent. "
            "You perform rigorous multi-step reasoning and execution."
        )

    def set_task(self, prompt: str) -> None:
        """Initialize the task prompt."""
        self.initial_prompt = prompt
        self.allocator.allocate(
            key="initial_prompt",
            content=prompt,
            importance=3.0,  # Never evict task goal
            metadata={"type": "task_instruction"},
        )

    def get_current_prompt_window(self) -> Dict[str, Any]:
        """Inspect the current active prompt window fed to the LLM.
        
        Demonstrates that prompt tokens stay lean and strictly bounded.
        """
        working_context = self.allocator.get_working_context_text()
        full_prompt = (
            f"SYSTEM: {self.system_instructions}\n\n"
            f"ACTIVE CONTEXT:\n{working_context}\n\n"
            f"TASK: {self.initial_prompt}"
        )
        token_count = estimate_sentencepiece_tokens(full_prompt)
        return {
            "full_prompt": full_prompt,
            "token_count": token_count,
            "working_tokens": self.allocator.get_active_prompt_tokens(),
            "working_limit": self.allocator.quotas[self.allocator.quotas.__iter__().__next__()].max_tokens,
        }

    def execute_step(
        self,
        phase: StepPhase,
        title: str,
        thought_content: str,
        thought_rationale: Optional[str] = None,
        action_type: Optional[str] = None,
        action_payload: Optional[Dict[str, Any]] = None,
        observation: Optional[str] = None,
        is_milestone: bool = False,
        tags: Optional[List[str]] = None,
    ) -> ProgressStep:
        """Execute a step in the reasoning pipeline.
        
        The verbose thought content and execution observations are captured
        OUT-OF-BAND by the tracker, never appended to the LLM prompt.
        """
        # Record step to out-of-band ledger
        step = self.tracker.track_step(
            phase=phase,
            title=title,
            thought_content=thought_content,
            thought_rationale=thought_rationale,
            action_type=action_type,
            action_payload=action_payload,
            observation=observation,
            is_milestone=is_milestone,
            tags=tags or [],
        )

        return step

    def query_memory_ondemand(self, query: str, top_k: int = 2) -> str:
        """Surgically retrieve past relevant memory without prompt bloat."""
        results = self.memory_agent.query_memory(query, top_k=top_k)
        if not results:
            return "No matching memory found."
        
        formatted = "\n".join(f"[{r['relevance']}] {r['content']}" for r in results)
        return formatted
