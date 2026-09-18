"""Qwen-Agent Framework Tool Definition for G-OmniOS.

Provides ready-to-use functions for Qwen-Agent or OpenAI-compatible tool callers.
"""

from typing import Dict, Any, Optional
from omni_memory.engine import GOmniOSSystem

# Singleton instance
_gomnios_instance: Optional[GOmniOSSystem] = None


def get_gomnios() -> GOmniOSSystem:
    global _gomnios_instance
    if _gomnios_instance is None:
        _gomnios_instance = GOmniOSSystem()
    return _gomnios_instance


def mind4action_cycle(stimulus: str) -> Dict[str, Any]:
    """Execute a 4-phase Mind4Action cognitive cycle for Qwen."""
    sys = get_gomnios()
    return sys.mind4action_cycle(stimulus)


def track_memory_step(title: str, thought: str, phase: str = "deliberation", is_milestone: bool = False) -> Dict[str, Any]:
    """Record an execution step out-of-band into LevelDB WAL to save tokens."""
    sys = get_gomnios()
    step = sys.step(phase=phase, title=title, thought=thought, is_milestone=is_milestone)
    return {
        "status": "success",
        "step_id": step.step_id,
        "token_weight": step.token_weight,
        "prompt_tokens_saved": sys.allocator.get_tokens_saved()
    }


def query_semantic_memory(query: str, top_k: int = 3) -> Dict[str, Any]:
    """Perform cosine semantic search over past thoughts and decisions via ScaNN."""
    sys = get_gomnios()
    results = sys.scann.search(query, top_k=top_k)
    return {
        "query": query,
        "results": [{"text": r.text, "score": r.score, "phase": r.phase.value} for r in results]
    }


def dispatch_agent_team(department: str, task: str) -> Dict[str, Any]:
    """Dispatch a task to a specialized agent department (manager, hr, fullstack, catalog, marketing, devops)."""
    sys = get_gomnios()
    return sys.dispatch_department(department, task)
