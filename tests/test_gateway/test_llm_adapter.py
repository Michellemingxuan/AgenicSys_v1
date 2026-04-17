"""Tests for LLM adapter ABC and OpenAI adapter."""

import pytest
from unittest.mock import MagicMock

from gateway.llm_adapter import BaseLLMAdapter


def test_base_adapter_is_abstract():
    with pytest.raises(TypeError):
        BaseLLMAdapter()


def test_openai_adapter_instantiation():
    mock_client = MagicMock()
    from gateway.openai_adapter import OpenAIAdapter

    adapter = OpenAIAdapter(client=mock_client)
    assert adapter.model == "gpt-4.1"
    assert adapter.client is mock_client
