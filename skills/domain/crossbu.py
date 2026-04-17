"""Cross-BU domain skill — cross-product exposure and contagion patterns."""

from models.types import DomainSkill


def get_skill() -> DomainSkill:
    return DomainSkill(
        name="crossbu",
        system_prompt=(
            "You are a cross-business-unit exposure analyst. You identify contagion patterns "
            "across product lines, aggregate exposures, and utilisation imbalances. "
            "Flag customers with concentrated risk in a single product or rapid exposure growth."
        ),
        data_hints=["xbu_summary"],
        interpretation_guide=(
            "High total exposure across multiple products increases contagion risk. "
            "Utilisation above 1.0 indicates over-limit usage. Compare product-level exposure "
            "to detect concentration."
        ),
        risk_signals=[
            "total exposure > 50k across products",
            "utilisation > 0.9 on any product",
            "single-product concentration > 80%",
        ],
    )
