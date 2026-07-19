"""Tests for Ollama AI services."""

import pytest
from unittest.mock import patch

from abia.ai.inference import EntityExtractor, CaseClassifier


class TestEntityExtractor:
    """Test entity extraction."""

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_extract_valid_json(self, mock_generate):
        """Given LLM returns valid JSON, parse entities."""
        mock_generate.return_value = (
            '{\"people\": [\"John Doe\"], '
            '\"locations\": [\"Aba\"], '
            '\"organizations\": [\"UNHCR\"]}'
        )

        result = EntityExtractor.extract_from_text("John Doe from Aba works with UNHCR")

        assert result["people"] == ["John Doe"]
        assert result["locations"] == ["Aba"]
        assert result["organizations"] == ["UNHCR"]

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_extract_with_code_block(self, mock_generate):
        """Given LLM wraps JSON in markdown, strip it."""
        mock_generate.return_value = (
            "```json\n"
            '{\"people\": [\"Jane\"], \"locations\": [], \"organizations\": []}'
            "\n```"
        )

        result = EntityExtractor.extract_from_text("Jane arrived yesterday")

        assert result["people"] == ["Jane"]

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_extract_invalid_json_fallback(self, mock_generate):
        """Given LLM returns garbage, return empty entities."""
        mock_generate.return_value = "not valid json"

        result = EntityExtractor.extract_from_text("some text")

        assert result == {"people": [], "locations": [], "organizations": []}

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_extract_ollama_down(self, mock_generate):
        """Given Ollama unreachable, return empty entities."""
        from urllib.error import URLError
        mock_generate.side_effect = URLError("Connection refused")

        result = EntityExtractor.extract_from_text("some text")

        assert result == {"people": [], "locations": [], "organizations": []}


class TestCaseClassifier:
    """Test case classification."""

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_classify_medical(self, mock_generate):
        """Given medical description, return medical."""
        mock_generate.return_value = "medical"

        result = CaseClassifier.classify_category("Patient has malaria")

        assert result == "medical"

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_classify_invalid_fallback(self, mock_generate):
        """Given invalid response, fallback to other."""
        mock_generate.return_value = "unknown category xyz"

        result = CaseClassifier.classify_category("some case")

        assert result == "other"

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_assess_priority_high(self, mock_generate):
        """Given urgent case, return high."""
        mock_generate.return_value = "high priority"

        result = CaseClassifier.assess_priority("Severe injury, needs surgery")

        assert result == "high"

    @patch("abia.ai.inference.OllamaClient.generate")
    def test_assess_priority_ollama_down(self, mock_generate):
        """Given Ollama down, fallback to medium."""
        from urllib.error import URLError
        mock_generate.side_effect = URLError("Connection refused")

        result = CaseClassifier.assess_priority("some case")

        assert result == "medium"
