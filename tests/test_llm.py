import pytest

from core import llm


def test_get_api_key_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert llm.get_api_key() is None


def test_get_api_key_returns_none_for_placeholder(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "your-api-key-here")
    assert llm.get_api_key() is None


def test_get_api_key_returns_trimmed_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "  AIza-test123  ")
    assert llm.get_api_key() == "AIza-test123"


def test_generate_raises_llm_error_without_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(llm.LLMError):
        llm.generate("hello", model=llm.DEFAULT_MODEL)


def test_models_dict_has_flash_default():
    assert llm.DEFAULT_MODEL == "gemini-3.5-flash"
    assert llm.DEFAULT_MODEL in llm.MODELS.values()
