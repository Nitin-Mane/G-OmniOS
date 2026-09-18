"""Memory Allocator and SentencePiece Token Governor for OmniMemory.

Enforces strict token quotas across memory tiers, ensuring the primary LLM
prompt window never bloats with intermediate progress steps or raw thoughts.
"""

from __future__ import annotations
import re
import time
from typing import Any, Dict, List, Optional
from omni_memory.models.memory_tier import (
    TierType,
    MemorySlot,
    TierQuota,
    MemoryAllocationReport,
)


def estimate_sentencepiece_tokens(text: str) -> int:
    """Estimate token count aligned with Google SentencePiece / Gemma tokenizers.
    
    Accounts for whitespace boundaries, subword prefixes, and code symbols.
    """
    if not text:
        return 0
    # Code symbols and punctuation often form individual tokens
    symbols = len(re.findall(r'[^\w\s]', text))
    # Words
    words = len(re.findall(r'\b\w+\b', text))
    # Whitespaces / newlines
    newlines = text.count('\n')
    
    # Heuristic matching SentencePiece average subword tokenization
    estimated = int((len(text) / 3.8) + (symbols * 0.2) + (newlines * 0.1))
    return max(1, estimated)


class MemoryAllocator:
    """Allocates, governs, and enforces memory budgets across tiers."""

    def __init__(
        self,
        working_limit: int = 800,
        episodic_limit: int = 3000,
    ):
        self.quotas: Dict[TierType, TierQuota] = {
            TierType.WORKING: TierQuota(max_tokens=working_limit, current_tokens=0),
            TierType.EPISODIC: TierQuota(max_tokens=episodic_limit, current_tokens=0),
            TierType.SEMANTIC: TierQuota(max_tokens=50000, current_tokens=0),
            TierType.ARCHIVAL: TierQuota(max_tokens=1000000, current_tokens=0),
        }
        
        # Live slot registry: slot_id -> MemorySlot
        self._slots: Dict[str, MemorySlot] = {}
        
        # Cumulative tracking of raw steps that were shielded from the prompt
        self._total_raw_tokens: int = 0
        self._session_id: str = "default_session"

    def set_session_id(self, session_id: str) -> None:
        self._session_id = session_id

    def record_raw_step_overhead(self, tokens: int) -> None:
        """Record raw tokens produced by intermediate thoughts & tools.
        
        These are preserved in the out-of-band ledger without entering the prompt.
        """
        self._total_raw_tokens += tokens

    def allocate(
        self,
        key: str,
        content: str,
        tier: TierType = TierType.WORKING,
        importance: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemorySlot:
        """Allocate a memory slot in the specified tier, respecting quotas."""
        token_cost = estimate_sentencepiece_tokens(content)
        now = time.time()
        
        slot_id = f"slot_{tier.value}_{key}_{int(now)}"
        slot = MemorySlot(
            slot_id=slot_id,
            tier=tier,
            key=key,
            content=content,
            token_cost=token_cost,
            created_at=now,
            last_accessed=now,
            importance=importance,
            metadata=metadata or {},
        )

        # If a slot with the same key already exists in this tier, replace it cleanly
        for sid, existing in list(self._slots.items()):
            if existing.tier == tier and existing.key == key:
                self.quotas[tier].current_tokens -= existing.token_cost
                del self._slots[sid]
                break

        quota = self.quotas[tier]
        
        # Eviction if working memory exceeds quota
        if tier == TierType.WORKING:
            while (quota.current_tokens + token_cost) > quota.max_tokens:
                evicted = self._evict_oldest_working_slot()
                if not evicted:
                    break

        self._slots[slot.slot_id] = slot
        quota.current_tokens += token_cost
        return slot

    def _evict_oldest_working_slot(self) -> bool:
        """Evict the least recently accessed slot from working memory to archival."""
        working_slots = [s for s in self._slots.values() if s.tier == TierType.WORKING]
        if not working_slots:
            return False
            
        # Find oldest / lowest importance
        oldest = min(working_slots, key=lambda s: (s.importance, s.last_accessed))
        
        # Demote to archival
        self.quotas[TierType.WORKING].current_tokens -= oldest.token_cost
        oldest.tier = TierType.ARCHIVAL
        self.quotas[TierType.ARCHIVAL].current_tokens += oldest.token_cost
        return True

    def get_working_context_text(self) -> str:
        """Construct the strictly bounded active context string for the prompt."""
        working_slots = [
            s for s in self._slots.values()
            if s.tier == TierType.WORKING
        ]
        # Sort by importance and access time
        working_slots.sort(key=lambda s: (s.importance, s.last_accessed), reverse=True)
        
        chunks = []
        for s in working_slots:
            chunks.append(f"[{s.key}]: {s.content}")
        return "\n\n".join(chunks)

    def get_active_prompt_tokens(self) -> int:
        """Current tokens consumed by the working prompt context."""
        return self.quotas[TierType.WORKING].current_tokens

    def generate_report(self) -> MemoryAllocationReport:
        """Generate real-time economics and token savings report."""
        active = self.get_active_prompt_tokens()
        raw = max(self._total_raw_tokens, active)
        saved = max(0, raw - active)
        savings_pct = round((saved / raw * 100.0), 1) if raw > 0 else 0.0

        distribution = {
            tier.value: sum(1 for s in self._slots.values() if s.tier == tier)
            for tier in TierType
        }

        return MemoryAllocationReport(
            session_id=self._session_id,
            working_tokens=active,
            working_limit=self.quotas[TierType.WORKING].max_tokens,
            episodic_count=distribution.get("episodic", 0),
            semantic_count=distribution.get("semantic", 0),
            archival_count=distribution.get("archival", 0),
            total_raw_tokens_generated=raw,
            active_prompt_tokens=active,
            tokens_saved=saved,
            savings_percentage=savings_pct,
            tier_distribution=distribution,
        )

    def clear(self) -> None:
        """Reset memory allocations."""
        self._slots.clear()
        for q in self.quotas.values():
            q.current_tokens = 0
        self._total_raw_tokens = 0
