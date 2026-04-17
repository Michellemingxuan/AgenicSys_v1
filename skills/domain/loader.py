"""Domain skill loader — discovers and loads domain skill modules."""

from __future__ import annotations

import importlib

from models.types import DomainSkill

_DOMAIN_MODULES = {
    "bureau": "skills.domain.bureau",
    "crossbu": "skills.domain.crossbu",
    "modeling": "skills.domain.modeling",
    "spend_payments": "skills.domain.spend_payments",
    "wcc": "skills.domain.wcc",
    "customer_rel": "skills.domain.customer_rel",
    "capacity_afford": "skills.domain.capacity_afford",
}


def load_domain_skill(name: str) -> DomainSkill | None:
    module_path = _DOMAIN_MODULES.get(name)
    if module_path is None:
        return None
    mod = importlib.import_module(module_path)
    return mod.get_skill()


def list_domain_skills() -> list[str]:
    return sorted(_DOMAIN_MODULES.keys())
