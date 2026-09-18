"""Multi-Agent Department Coordinator for G-OmniOS.

Provides unified orchestration across Catalog, Marketing, DevOps, Fullstack AI,
Manager, and HR agent teams.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional

from omni_memory.departments.manager_agent import ManagerAgent
from omni_memory.departments.hr_agent import HRAgent
from omni_memory.departments.fullstack_ai_agent import FullstackAIAgent
from omni_memory.departments.catalog_agent import CatalogAgent
from omni_memory.departments.marketing_agent import MarketingAgent
from omni_memory.departments.devops_agent import DevOpsAgent


class DepartmentCoordinator:
    """Unified dispatcher for G-OmniOS organizational agent teams."""

    def __init__(self):
        self.manager = ManagerAgent()
        self.hr = HRAgent()
        self.fullstack = FullstackAIAgent()
        self.catalog = CatalogAgent()
        self.marketing = MarketingAgent()
        self.devops = DevOpsAgent()

    def get_team_roster(self) -> List[Dict[str, Any]]:
        """Return the active agent department roster and status."""
        return [
            {"id": "manager", "name": "Manager Agent", "title": "Manager Agent", "role": self.manager.role, "track": "Social/Strategy", "focus": "Sprint roadmaps, deliverables, token KPIs", "status": "ACTIVE"},
            {"id": "hr", "name": "HR Agent", "title": "HR Agent", "role": self.hr.role, "track": "Mental/Safety", "focus": "Psychological safety, ergonomics, burnout alerts", "status": "ACTIVE"},
            {"id": "fullstack", "name": "Fullstack AI Agent", "title": "Fullstack AI Agent", "role": self.fullstack.role, "track": "Technical", "focus": "Memory engine, Mind4Action cycle, ScaNN/LevelDB", "status": "ACTIVE"},
            {"id": "catalog", "name": "Catalog Agent", "title": "Catalog Agent", "role": self.catalog.role, "track": "All Tracks", "focus": "Persona skills curation (Tech, Social, Mental)", "status": "ACTIVE"},
            {"id": "marketing", "name": "Marketing Agent", "title": "Marketing Agent", "role": self.marketing.role, "track": "Social/Product", "focus": "Positioning, value propositions, feature messaging", "status": "ACTIVE"},
            {"id": "devops", "name": "DevOps Agent", "title": "DevOps Agent", "role": self.devops.role, "track": "Technical", "focus": "Watchdog daemon, ports, latency, zero-cloud uptime", "status": "ACTIVE"},
        ]

    def get_roster(self) -> Dict[str, Dict[str, Any]]:
        """Return dictionary mapping department id to info."""
        return {item["id"]: item for item in self.get_team_roster()}

    def dispatch(
        self,
        department: str,
        task: str = "status",
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dispatch a task or query to a specialized department agent."""
        dept = department.lower().strip()
        data = payload or {}

        res: Dict[str, Any]
        if dept in ("manager", "management"):
            if task == "plan":
                res = self.manager.plan_objective(data.get("objective", "Deliver G-OmniOS"))
            else:
                res = self.manager.generate_sprint_report(data.get("telemetry"))

        elif dept in ("hr", "people", "safety"):
            if "cognitive_state" in data:
                res = self.hr.assess_wellbeing(data["cognitive_state"])
            elif hasattr(data.get("state"), "cognitive_load_index"):
                res = self.hr.assess_wellbeing(data["state"])
            else:
                res = {
                    "agent": "HRAgent",
                    "role": self.hr.role,
                    "status": "Psychological safety guards active.",
                    "timestamp": time.time()
                }

        elif dept in ("fullstack", "fullstack_ai", "ai", "engineering"):
            res = self.fullstack.audit_memory_architecture(data.get("telemetry", {}))

        elif dept in ("catalog", "product", "skills"):
            res = self.catalog.list_all_skills()

        elif dept in ("marketing", "growth", "positioning"):
            res = self.marketing.generate_value_briefing(data.get("telemetry", {}))

        elif dept in ("devops", "infra", "ops"):
            port = int(data.get("port", 8765))
            res = self.devops.check_system_health(port=port)

        else:
            return {
                "error": f"Unknown department: '{department}'. Available: manager, hr, fullstack, catalog, marketing, devops",
                "roster": self.get_team_roster()
            }

        res["department"] = dept
        res.setdefault("status", "SUCCESS")
        return res
