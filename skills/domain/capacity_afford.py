"""Capacity & Affordability domain skill — DTI, limit headroom, income capacity."""

from models.types import DomainSkill


def get_skill() -> DomainSkill:
    return DomainSkill(
        name="capacity_afford",
        system_prompt=(
            "You are a capacity and affordability analyst. You evaluate debt-to-income ratios, "
            "credit-limit headroom, income stability, and overall affordability. Identify "
            "customers who are over-leveraged or approaching affordability limits."
        ),
        data_hints=["income_dti"],
        interpretation_guide=(
            "DTI above 0.43 is a common regulatory threshold. Limited headroom combined "
            "with high DTI signals stress. Income volatility adds uncertainty to "
            "affordability assessments."
        ),
        risk_signals=[
            "DTI > 0.43",
            "limit headroom < 10%",
            "income decline > 15% year-over-year",
        ],
    )
