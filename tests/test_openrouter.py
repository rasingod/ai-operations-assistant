"""OpenRouter transport, configuration and fail-closed provider errors."""
from pathlib import Path
from types import SimpleNamespace
import httpx
import pytest
from openai import APIStatusError, APIConnectionError
from ops_assistant import config
from ops_assistant.agent import Assistant
from ops_assistant.router import LLMRouter
from ops_assistant.router import PlannerError
from ops_assistant.store import Store

@pytest.fixture
def settings_env(monkeypatch):
    monkeypatch.setattr(config, 'load_dotenv', lambda *args: None)
    for key in ('OPENROUTER_API_KEY','OPENROUTER_MODEL','ASSISTANT_MODE'):
        monkeypatch.delenv(key, raising=False)
    return monkeypatch

def test_openrouter_configuration(settings_env):
    settings_env.setenv('ASSISTANT_MODE','llm')
    settings_env.setenv('OPENROUTER_API_KEY','unit-test-credential')
    settings = config.Settings.load()
    assert settings.model == 'openai/gpt-4.1-mini'
    assert settings.base_url == 'https://openrouter.ai/api/v1'
    assert 'unit-test-credential' not in repr(settings)
    router = LLMRouter(settings)
    assert str(router.client.base_url) == 'https://openrouter.ai/api/v1/'
    assert router.client.max_retries == 1
    router.client.close()

def test_openrouter_key_required(settings_env):
    settings_env.setenv('ASSISTANT_MODE','llm')
    settings_env.setenv('OPENAI_API_KEY','unrelated-key')
    with pytest.raises(ValueError,match='OPENROUTER_API_KEY'):
        config.Settings.load()

@pytest.mark.parametrize('model',['','gpt-4.1-mini','openai /model'])
def test_invalid_model_slug(settings_env,model):
    settings_env.setenv('OPENROUTER_MODEL',model)
    with pytest.raises(ValueError,match='provider/model'):
        config.Settings.load()

@pytest.mark.parametrize('status,phrase',[(401,'rejected the API key'),(402,'credits are insufficient'),
    (429,'rate limited'),(400,'model configuration'),(404,'unavailable'),(403,'denied'),(503,'temporarily unavailable')])
def test_provider_failures_take_no_action(tmp_path,status,phrase):
    router = LLMRouter.__new__(LLMRouter)
    router.model = 'openai/gpt-4.1-mini'
    def fail(**kwargs):
        response = httpx.Response(status,request=httpx.Request('POST','https://openrouter.ai/api/v1/chat/completions'))
        raise APIStatusError('sensitive-response',response=response,body={'secret':'do-not-display'})
    router.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    store = Store(tmp_path/'errors.db',Path(__file__).resolve().parents[1]/'data/seed.json')
    result = Assistant(store,router,'EMP1024').chat('Please raise a ticket for a broken printer')
    assert phrase in result['reply']
    assert 'No action was taken' in result['reply']
    assert 'sensitive' not in result['reply'] and 'do-not-display' not in result['reply']
    assert len(store.lookup('EMP1024')) == 2

def test_transport_failure_is_safe(tmp_path):
    router = LLMRouter.__new__(LLMRouter)
    router.model = 'openai/gpt-4.1-mini'
    def fail(**kwargs):
        raise APIConnectionError(request=httpx.Request('POST','https://openrouter.ai/api/v1/chat/completions'))
    router.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    store = Store(tmp_path/'connection.db',Path(__file__).resolve().parents[1]/'data/seed.json')
    assert 'Could not reach OpenRouter' in Assistant(store,router,'EMP1024').chat('VPN help')['reply']

@pytest.mark.parametrize('recover',[True,False])
def test_malformed_output_has_one_bounded_correction(recover):
    router = LLMRouter.__new__(LLMRouter)
    router.model = 'openrouter/free'
    requests = []
    def create(**kwargs):
        requests.append(kwargs)
        calls = []
        if recover and len(requests) == 2:
            calls = [SimpleNamespace(function=SimpleNamespace(name='knowledge_search',
                arguments='{"query":"VPN help","title":"","description":""}'))]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=calls))])
    router.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    if recover:
        assert router.decide('VPN help',{}).name == 'knowledge_search'
    else:
        with pytest.raises(PlannerError,match='twice'):
            router.decide('VPN help',{})
    assert len(requests) == 2
    assert 'Output correction' in requests[1]['messages'][0]['content']
