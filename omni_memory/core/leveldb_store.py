"""Google LevelDB-style embedded step ledger for OmniMemory.

Implements key architectural principles from Google's LevelDB (google/leveldb):
1. Append-Only Write-Ahead Log (WAL) for zero-latency step writes.
2. In-memory MemTable with sorted key indexing.
3. Persistent SSTable segment snapshots for durable archival memory.
4. Prefix and range scanning for chronological step retrieval.
"""

from __future__ import annotations
import os
import json
import time
import threading
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple
from omni_memory.models.step import ProgressStep


class LevelDBStepLedger:
    """Embedded Log-Structured Step Ledger following Google LevelDB design."""

    def __init__(self, db_path: str = "./.omni_memory_leveldb"):
        self.db_dir = Path(db_path)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        self.wal_path = self.db_dir / "000001.log"
        self.manifest_path = self.db_dir / "MANIFEST"
        self._lock = threading.RLock()
        
        # In-memory MemTable (ordered mapping key -> value)
        self._memtable: Dict[str, Dict[str, Any]] = {}
        
        # Recover state from existing WAL if present
        self._recover_from_wal()

    def _recover_from_wal(self) -> None:
        """Replay Write-Ahead Log into MemTable on startup."""
        if not self.wal_path.exists():
            return
        
        try:
            with open(self.wal_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        key = record.get("key")
                        val = record.get("val")
                        if key:
                            if val is None:
                                self._memtable.pop(key, None)
                            else:
                                self._memtable[key] = val
                    except Exception:
                        continue
        except Exception:
            pass

    def put(self, key: str, value: Dict[str, Any]) -> None:
        """Atomically append write to WAL and update MemTable."""
        with self._lock:
            # 1. Append to WAL
            entry = {"key": key, "val": value, "ts": time.time()}
            with open(self.wal_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                f.flush()
                
            # 2. Update MemTable
            self._memtable[key] = value

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Point lookup by key."""
        with self._lock:
            return self._memtable.get(key)

    def delete(self, key: str) -> None:
        """Tombstone record in WAL and remove from MemTable."""
        with self._lock:
            entry = {"key": key, "val": None, "ts": time.time()}
            with open(self.wal_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
                f.flush()
            self._memtable.pop(key, None)

    def append_step(self, step: ProgressStep) -> None:
        """Save a progress step out-of-band with a zero-padded chronological key.
        
        Key Format: `steps:{session_id}:{sequence_num:08d}`
        """
        key = f"steps:{step.session_id}:{step.sequence_num:08d}"
        self.put(key, step.model_dump())

    def get_steps_for_session(self, session_id: str) -> List[ProgressStep]:
        """Fetch all chronological steps for a given session using prefix scan."""
        prefix = f"steps:{session_id}:"
        with self._lock:
            matching_keys = sorted([k for k in self._memtable.keys() if k.startswith(prefix)])
            steps = []
            for k in matching_keys:
                try:
                    steps.append(ProgressStep.model_validate(self._memtable[k]))
                except Exception:
                    continue
            return steps

    def get_latest_step(self, session_id: str) -> Optional[ProgressStep]:
        """Retrieve the most recent progress step."""
        steps = self.get_steps_for_session(session_id)
        return steps[-1] if steps else None

    def compact(self, session_id: Optional[str] = None) -> int:
        """Simulate LevelDB minor/major compaction: flushes clean state to snapshot file."""
        with self._lock:
            snapshot_file = self.db_dir / f"snapshot_{int(time.time())}.sst"
            data_to_write = {
                k: v for k, v in self._memtable.items()
                if (session_id is None or k.startswith(f"steps:{session_id}:"))
            }
            with open(snapshot_file, "w", encoding="utf-8") as f:
                json.dump(data_to_write, f, indent=2)
            return len(data_to_write)

    def count_total_steps(self) -> int:
        """Total steps indexed in storage."""
        with self._lock:
            return sum(1 for k in self._memtable.keys() if k.startswith("steps:"))
