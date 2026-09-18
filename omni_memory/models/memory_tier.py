"""Memory tier definitions and allocation quotas for Google OmniMemory.

Implements SentencePiece-driven budget enforcement across 4 memory tiers:
1. WORKING: Active prompt slot (strictly bounded, zero bloat).
2. EPISODIC: Consolidated milestones (ReasoningBank).
3. SEMANTIC: Vector-indexed knowledge (Google ScaNN).
4. ARCHIVAL: Out-of-band persistent logs (Google LevelDB).
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TierType(str, Enum):
    WORKING = "working"        # Active in-prompt context (strictly budgeted)
    EPISODIC = "episodic"      # Consolidated milestones & strategy memory
    SEMANTIC = "semantic"      # Vector-indexed facts queried on-demand (ScaNN)
    ARCHIVAL = "archival"      # Out-of-band persistent raw logs (LevelDB)


class MemorySlot(BaseModel):
    """An allocated memory entry in a specific tier."""
    slot_id: str
    tier: TierType
    key: str
    content: str
    token_cost: int
    created_at: float = Field(default_factory=time.time)
    last_accessed: float = Field(default_factory=time.time)
    importance: float = 1.0
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TierQuota(BaseModel):
    """Budget limits for each memory tier."""
    max_tokens: int
    current_tokens: int = 0
    eviction_policy: str = "lru"  # "lru", "importance", or "abstract"


class MemoryAllocationReport(BaseModel):
    """Real-time report of memory consumption and prompt token savings."""
    session_id: str
    working_tokens: int
    working_limit: int
    episodic_count: int
    semantic_count: int
    archival_count: int
    
    # Economics:
    total_raw_tokens_generated: int     # What standard unbuffered LLM prompts would hold
    active_prompt_tokens: int           # What the prompt actually contains (strictly bounded)
    tokens_saved: int                   # Raw - Active
    savings_percentage: float           # e.g., 88.5%
    
    tier_distribution: Dict[str, int] = Field(default_factory=dict)
