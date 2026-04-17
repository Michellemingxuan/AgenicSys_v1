"""Spend & Payments domain skill — payment trends, delinquency, spend spikes."""

from models.types import DomainSkill


def get_skill() -> DomainSkill:
    return DomainSkill(
        name="spend_payments",
        system_prompt=(
            "You are a spend and payments analyst. You examine monthly transaction volumes, "
            "payment patterns, delinquency history, and spend spikes. Identify customers "
            "showing early delinquency signals or unusual spending behaviour."
        ),
        data_hints=["txn_monthly", "pmts_detail"],
        interpretation_guide=(
            "Rising spend with declining payments is a classic early-warning pattern. "
            "Look for minimum-payment-only behaviour and sudden spend spikes that may "
            "indicate financial stress or fraud."
        ),
        risk_signals=[
            "payment < minimum due for 2+ months",
            "spend spike > 3x average",
            "declining payment ratio trend",
            "days-past-due increasing",
        ],
    )
