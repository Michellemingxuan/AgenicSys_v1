"""Modeling domain skill — score trajectories and model signals."""

from models.types import DomainSkill


def get_skill() -> DomainSkill:
    return DomainSkill(
        name="modeling",
        system_prompt=(
            "You are a model-performance and score-trajectory analyst. You interpret "
            "model scores, track score migration over time, and identify customers whose "
            "risk trajectory is deteriorating or improving. Compare model outputs to "
            "bureau data for consistency."
        ),
        data_hints=["model_scores"],
        interpretation_guide=(
            "Falling scores over consecutive periods signal deterioration. "
            "Divergence between model score and bureau score may indicate model staleness "
            "or emerging risk not yet reflected in bureau."
        ),
        risk_signals=[
            "score drop > 50 points in 3 months",
            "model score diverges from bureau score by > 100 points",
            "score in bottom decile",
        ],
    )
