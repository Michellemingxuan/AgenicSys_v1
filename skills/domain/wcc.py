"""WCC domain skill — watch-list flags and control signals."""

from models.types import DomainSkill


def get_skill() -> DomainSkill:
    return DomainSkill(
        name="wcc",
        system_prompt=(
            "You are a watch-list and compliance-controls analyst. You review WCC flags, "
            "sanctions screening results, and control signals. Identify customers with "
            "active flags that require escalation or enhanced due diligence."
        ),
        data_hints=["wcc_flags"],
        interpretation_guide=(
            "Any active WCC flag requires immediate attention. Multiple flags or "
            "flags across different screening categories compound risk. "
            "Cleared flags with recent re-hits should be treated as elevated risk."
        ),
        risk_signals=[
            "active WCC flag",
            "multiple flag categories",
            "recently cleared flag with re-hit",
        ],
    )
