"""AI inference services for entity extraction and case classification.

Per Architecture Contract §2.3:
Ollama local LLM for NLP (entity extraction, classification).
"""

import json
import logging
import re

from abia.common.ollama_client import OllamaClient

logger = logging.getLogger("abia.ai.inference")


class EntityExtractor:
    """Extract entities from ODK submissions and officer notes."""

    @staticmethod
    def extract_from_text(text: str) -> dict:
        """Extract people, locations, organizations from text.

        Args:
            text: Raw text (e.g., officer notes, ODK submission).

        Returns:
            dict: {"people": [...], "locations": [...], "organizations": [...]}
        """
        system_prompt = (
            "You are an entity extraction engine. "
            "Extract only people, locations, and organizations from the text. "
            "Respond ONLY with valid JSON in this exact format: "
            '{\"people\": [], \"locations\": [], \"organizations\": []}'
        )

        try:
            response = OllamaClient.generate(
                prompt=f"Extract entities from: {text}",
                system=system_prompt,
            )
            # Strip markdown code blocks if present
            clean = re.sub(r"```json\s*|```\s*", "", response).strip()
            return json.loads(clean)
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("Entity extraction failed: %s", exc)
            return {"people": [], "locations": [], "organizations": []}


class CaseClassifier:
    """Classify cases by type and priority using LLM."""

    CATEGORY_PROMPT = (
        "Classify this migrant case into ONE category: "
        "medical, legal, economic, protection, education, other. "
        "Respond with ONLY the category name, nothing else."
    )

    PRIORITY_PROMPT = (
        "Assess the urgency of this case. "
        "Respond with ONLY one word: low, medium, high, or critical."
    )

    @staticmethod
    def classify_category(description: str) -> str:
        """Classify case into category."""
        try:
            result = OllamaClient.generate(
                prompt=f"Case description: {description}",
                system=CaseClassifier.CATEGORY_PROMPT,
            )
            category = result.strip().lower().split()[0]
            valid = {"medical", "legal", "economic", "protection", "education", "other"}
            return category if category in valid else "other"
        except Exception as exc:
            logger.warning("Category classification failed: %s", exc)
            return "other"

    @staticmethod
    def assess_priority(description: str) -> str:
        """Assess case priority."""
        try:
            result = OllamaClient.generate(
                prompt=f"Case description: {description}",
                system=CaseClassifier.PRIORITY_PROMPT,
            )
            priority = result.strip().lower().split()[0]
            valid = {"low", "medium", "high", "critical"}
            return priority if priority in valid else "medium"
        except Exception as exc:
            logger.warning("Priority assessment failed: %s", exc)
            return "medium"
