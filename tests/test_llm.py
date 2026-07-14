import pytest

from core import llm


def test_get_api_key_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert llm.get_api_key() is None


def test_get_api_key_returns_none_for_placeholder(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "your-api-key-here")
    assert llm.get_api_key() is None


def test_get_api_key_returns_trimmed_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  sk-ant-test123  ")
    assert llm.get_api_key() == "sk-ant-test123"


def test_generate_raises_llm_error_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(llm.LLMError):
        llm.generate("hello", model=llm.DEFAULT_MODEL)


def test_models_dict_has_haiku_default():
    assert llm.DEFAULT_MODEL == "claude-haiku-4-5"
    assert llm.DEFAULT_MODEL in llm.MODELS.values()
