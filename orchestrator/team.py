"""Team construction — selects relevant specialists for a question."""

from __future__ import annotations

import json

from gateway.firewall_stack import FirewallStack
from log.event_logger import EventLogger


TEAM_CONSTRUCTION_PROMPT = (
    "You are a team construction agent. Given a question, a pillar context, "
    "a list of available specialist domains, and a list of currently active "
    "specialists (warm, with context), select the most relevant specialists "
    "to answer the question.\n\n"
    "Guidelines:\n"
    "- Be targeted, not exhaustive — only select specialists whose domain "
    "is directly relevant to the question.\n"
    "- Prefer warm specialists (already active with context) when they are "
    "relevant, as they carry prior analysis.\n"
    "- Return a JSON object: {\"specialists\": [\"domain1\", \"domain2\"]}\n"
    "- Always return at least one specialist."
)


class TeamConstructor:
    """Selects relevant specialists for a given question."""

    def __init__(self, firewall: FirewallStack, logger: EventLogger):
        self.firewall = firewall
        self.logger = logger

    def select_specialists(
        self,
        question: str,
        pillar: str,
        available_specialists: list[str],
        active_specialists: list[dict],
    ) -> list[str]:
        self.logger.log(
            "team_construction_start",
            {"question": question, "pillar": pillar, "available": available_specialists},
        )

        user_message = (
            f"Question: {question}\n"
            f"Pillar: {pillar}\n"
            f"Available specialists: {available_specialists}\n"
            f"Active specialists (warm): {json.dumps(active_specialists)}\n\n"
            "Select the relevant specialists for this question."
        )

        result = self.firewall.call(
            system_prompt=TEAM_CONSTRUCTION_PROMPT,
            user_message=user_message,
        )

        if result.status == "blocked" or result.data is None:
            self.logger.log("team_construction_fallback", {"reason": "blocked"})
            return available_specialists

        selected = self._parse_selection(result.data, available_specialists)

        self.logger.log("team_construction_done", {"selected": selected})
        return selected

    def _parse_selection(
        self, data: dict, available: list[str]
    ) -> list[str]:
        raw = data.get("specialists", data.get("response", ""))

        if isinstance(raw, list):
            names = raw
        elif isinstance(raw, str):
            # Try to parse JSON from the response string
            try:
                parsed = json.loads(raw)
                names = parsed.get("specialists", [])
            except (json.JSONDecodeError, AttributeError):
                return available
        else:
            return available

        # Validate against available list
        validated = [n for n in names if n in available]
        if not validated:
            return available

        return validated
