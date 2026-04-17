"""Customer Relationship domain skill — tenure, product usage, relationship depth."""

from models.types import DomainSkill


def get_skill() -> DomainSkill:
    return DomainSkill(
        name="customer_rel",
        system_prompt=(
            "You are a customer-relationship analyst. You evaluate tenure, product breadth, "
            "engagement depth, and relationship value. Identify customers whose relationship "
            "profile suggests retention value or those showing signs of disengagement."
        ),
        data_hints=["cust_tenure"],
        interpretation_guide=(
            "Long tenure with multiple products indicates a valuable relationship. "
            "Declining product usage or account closures may signal disengagement. "
            "New customers with rapid product adoption may warrant closer monitoring."
        ),
        risk_signals=[
            "tenure < 6 months with high exposure",
            "product count declining",
            "relationship value below profitability threshold",
        ],
    )
