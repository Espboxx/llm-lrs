import pytest

from services.ai_decision import AIDecisionService


def make_service():
    # 绕过 __init__ 以避免初始化真实 OpenAI 客户端
    return AIDecisionService.__new__(AIDecisionService)


def test_normalize_none_like_target_returns_none():
    service = make_service()
    game_state = {'players': {'player1': object()}}

    result = service._normalize_decision({'target_id': 'none'}, game_state)

    assert result['target_id'] is None


def test_normalize_matches_known_player_case_insensitive():
    service = make_service()
    game_state = {'players': {'player5': object()}}

    result = service._normalize_decision({'target_id': 'PLAYER5'}, game_state)

    assert result['target_id'] == 'player5'


def test_normalize_invalid_player_returns_none():
    service = make_service()
    game_state = {'players': {'player5': object()}}

    result = service._normalize_decision({'target_id': 'ghost'}, game_state)

    assert result['target_id'] is None


def test_parse_response_handles_multiline_json():
    service = make_service()
    response_text = """
    <think>reasoning</think>
    {
        "target_id": "player3"
    }
    """

    result = service._parse_response(response_text)

    assert result['target_id'] == 'player3'


def test_parse_response_invalid_json_logs_error(caplog):
    service = make_service()

    with caplog.at_level('ERROR'):
        result = service._parse_response("<think></think>{ not json }")

    assert result['target_id'] is None
    assert any('JSON解析失败' in record.message for record in caplog.records)


class DummyResponse:
    def __init__(self, contents):
        self.choices = [DummyChoice(content) for content in contents]


class DummyChoice:
    def __init__(self, content):
        self.message = DummyMessage(content)


class DummyMessage:
    def __init__(self, content):
        self.content = content


def test_extract_choice_content_returns_first_non_empty():
    service = make_service()
    response = DummyResponse([None, "", "最终内容"])

    result = service._extract_choice_content(response, context="action")

    assert result == "最终内容"


def test_extract_choice_content_missing_returns_none(caplog):
    service = make_service()
    response = DummyResponse([None, ""])

    with caplog.at_level('ERROR'):
        result = service._extract_choice_content(response, context="speech")

    assert result is None
    assert any('缺少内容' in record.message for record in caplog.records)


def test_init_openai_provider_uses_default_endpoint(monkeypatch):
    captured_kwargs = {}

    class DummyClient:
        def __init__(self, **kwargs):
            captured_kwargs.update(kwargs)

    monkeypatch.setenv('AI_PROVIDER', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', 'fake-key')
    monkeypatch.delenv('OPENAI_BASE_URL', raising=False)
    monkeypatch.setattr('services.ai_decision.OpenAI', DummyClient)

    AIDecisionService()

    assert captured_kwargs == {'api_key': 'fake-key'}


def test_init_custom_provider_sets_default_base_url(monkeypatch):
    captured_kwargs = {}

    class DummyClient:
        def __init__(self, **kwargs):
            captured_kwargs.update(kwargs)

    monkeypatch.setenv('AI_PROVIDER', 'ollama')
    monkeypatch.delenv('OPENAI_BASE_URL', raising=False)
    monkeypatch.setattr('services.ai_decision.OpenAI', DummyClient)

    AIDecisionService()

    assert captured_kwargs['api_key'] == 'not-needed'
    assert captured_kwargs['base_url'] == 'http://localhost:11434/v1'
