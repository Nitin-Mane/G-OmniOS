"""G-OmniOS organizational multi-agent departments."""

from omni_memory.departments.manager_agent import ManagerAgent
from omni_memory.departments.hr_agent import HRAgent
from omni_memory.departments.fullstack_ai_agent import FullstackAIAgent
from omni_memory.departments.catalog_agent import CatalogAgent
from omni_memory.departments.marketing_agent import MarketingAgent
from omni_memory.departments.devops_agent import DevOpsAgent
from omni_memory.departments.coordinator import DepartmentCoordinator

__all__ = [
    "ManagerAgent",
    "HRAgent",
    "FullstackAIAgent",
    "CatalogAgent",
    "MarketingAgent",
    "DevOpsAgent",
    "DepartmentCoordinator",
]
