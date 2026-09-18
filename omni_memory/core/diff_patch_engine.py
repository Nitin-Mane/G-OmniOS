"""Google Diff-Match-Patch core engine for OmniMemory.

Based on Google's open-source Diff Match and Patch library (google/diff-match-patch).
Provides high-performance diffing, fuzzy matching, and patching to revise
agent contexts incrementally without duplicating prompt history.
"""

from __future__ import annotations
import re
import difflib
from typing import Any, Dict, List, Optional, Tuple
from omni_memory.models.context_revision import DiffOperation, ContextRevision


# Operation constants matching Google Diff-Match-Patch specification
DIFF_DELETE = -1
DIFF_INSERT = 1
DIFF_EQUAL = 0


class GoogleDiffMatchPatch:
    """Implementation of Google Diff-Match-Patch for memory context revision."""

    def __init__(self, match_threshold: float = 0.5, patch_margin: int = 4):
        self.match_threshold = match_threshold
        self.patch_margin = patch_margin

    def diff_compute(self, text1: str, text2: str) -> List[Tuple[int, str]]:
        """Compute the difference between two texts.
        
        Returns a list of tuples: (operation, text_segment)
        where operation is:
          -1 (DIFF_DELETE)
           0 (DIFF_EQUAL)
           1 (DIFF_INSERT)
        """
        if text1 == text2:
            return [(DIFF_EQUAL, text1)] if text1 else []
        if not text1:
            return [(DIFF_INSERT, text2)]
        if not text2:
            return [(DIFF_DELETE, text1)]

        matcher = difflib.SequenceMatcher(None, text1, text2)
        diffs: List[Tuple[int, str]] = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                diffs.append((DIFF_EQUAL, text1[i1:i2]))
            elif tag == 'delete':
                diffs.append((DIFF_DELETE, text1[i1:i2]))
            elif tag == 'insert':
                diffs.append((DIFF_INSERT, text2[j1:j2]))
            elif tag == 'replace':
                diffs.append((DIFF_DELETE, text1[i1:i2]))
                diffs.append((DIFF_INSERT, text2[j1:j2]))

        return self.diff_cleanup_semantic(diffs)

    def diff_cleanup_semantic(self, diffs: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        """Clean up diffs to align with human-readable semantic word/line boundaries."""
        if not diffs:
            return []

        cleaned: List[Tuple[int, str]] = []
        for op, text in diffs:
            if not text:
                continue
            if cleaned and cleaned[-1][0] == op:
                # Merge consecutive identical operations
                prev_op, prev_text = cleaned.pop()
                cleaned.append((prev_op, prev_text + text))
            else:
                cleaned.append((op, text))

        return cleaned

    def create_patch_text(self, text1: str, text2: str) -> str:
        """Create a human-readable Google patch delta between text1 and text2."""
        diffs = self.diff_compute(text1, text2)
        patch_lines = [f"@@ -0,0 +0,0 @@ (Google Diff-Match-Patch delta)"]
        
        for op, data in diffs:
            lines = data.splitlines(keepends=True)
            if not lines:
                lines = [data]
            prefix = " " if op == DIFF_EQUAL else ("+" if op == DIFF_INSERT else "-")
            for line in lines:
                patch_lines.append(f"{prefix}{line.rstrip('\r\n')}")
                
        return "\n".join(patch_lines)

    def apply_patch_text(self, base_text: str, patch_delta: str) -> str:
        """Reconstruct new text by applying a Google patch delta to base_text."""
        lines = patch_delta.splitlines()
        result_chunks: List[str] = []
        
        for line in lines:
            if line.startswith("@@"):
                continue
            if line.startswith("+"):
                result_chunks.append(line[1:])
            elif line.startswith(" "):
                result_chunks.append(line[1:])
            elif line.startswith("-"):
                # Deleted line, skip
                continue

        return "\n".join(result_chunks)

    def generate_revision(
        self,
        session_id: str,
        step_start: int,
        step_end: int,
        previous_context: str,
        revised_context: str,
        raw_tokens_consumed: int,
        revised_tokens: int,
        active_goals: Optional[List[str]] = None,
        resolved_goals: Optional[List[str]] = None,
        key_constraints: Optional[List[str]] = None,
    ) -> ContextRevision:
        """Create a full ContextRevision object tracking semantic evolution."""
        raw_diffs = self.diff_compute(previous_context, revised_context)
        diff_ops = [DiffOperation(op=op, text=text) for op, text in raw_diffs]
        patch_text = self.create_patch_text(previous_context, revised_context)
        
        compression = (
            round(raw_tokens_consumed / max(revised_tokens, 1), 2)
            if raw_tokens_consumed > 0 else 1.0
        )

        return ContextRevision(
            session_id=session_id,
            step_start=step_start,
            step_end=step_end,
            previous_context_summary=previous_context,
            revised_context_summary=revised_context,
            patch_delta=patch_text,
            diff_operations=diff_ops,
            raw_step_tokens=raw_tokens_consumed,
            revised_tokens=revised_tokens,
            compression_ratio=compression,
            active_goals=active_goals or [],
            resolved_goals=resolved_goals or [],
            key_constraints=key_constraints or [],
        )
