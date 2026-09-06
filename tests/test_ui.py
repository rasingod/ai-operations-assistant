from streamlit.testing.v1 import AppTest
from pathlib import Path

def test_streamlit_chat_and_reset(tmp_path,monkeypatch):
    monkeypatch.setenv('ASSISTANT_MODE','demo')
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'ui.db'))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run(timeout=30)
    assert not app.exception
    app.chat_input[0].set_value('What is the status of my laptop issue?').run()
    assert not app.exception
    assert any('IT-1001' in item.value for item in app.text)
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state['events'] == []
