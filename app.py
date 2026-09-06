"""Streamlit entry point. Run: streamlit run app.py"""
import logging
import os
import streamlit as st
from ops_assistant.agent import Assistant
from ops_assistant.config import ROOT, Settings
from ops_assistant.router import DemoRouter, LLMRouter
from ops_assistant.store import Store

st.set_page_config(page_title='Northstar IT Assistant', page_icon='🛠️', layout='centered')
logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO'),format='%(asctime)s %(levelname)s %(name)s %(message)s')
st.title('Northstar IT Assistant')
st.caption('AI Operations Assistant · Project 3')
try:
    settings = Settings.load()
    store = Store(settings.database, ROOT / 'data/seed.json')
except Exception:
    st.error('Startup failed. Check .env settings and database folder permissions. See README troubleshooting.')
    st.stop()

with st.sidebar:
    st.header('Workspace')
    st.info('Fictional organization. Profile selection is for local demonstration, not authentication.')
    profiles = store.employees()
    employee_id = st.selectbox('Employee profile', [p['id'] for p in profiles],
        format_func=lambda value: next(f"{p['name']} ({value})" for p in profiles if p['id']==value))
    st.caption(f'Mode: {settings.mode.upper()}')
    if settings.mode == 'demo':
        st.warning('Offline rules mode. Enable LLM mode for the GenAI evaluation.')
    else:
        st.caption('Messages and recent conversation context are sent to the configured model provider.')
    reset = st.button('Clear conversation',use_container_width=True)
    st.caption('Clearing chat discards its draft. Saved tickets remain in SQLite.')

key = (employee_id,settings.mode,settings.model,str(settings.database))
if st.session_state.get('assistant_key') != key or reset:
    router = LLMRouter(settings) if settings.mode == 'llm' else DemoRouter()
    st.session_state.assistant = Assistant(store,router,employee_id)
    st.session_state.assistant_key = key
    st.session_state.events = []

assistant = st.session_state.assistant
if not assistant.state['history']:
    st.write('Ask for IT guidance, check a ticket, or describe an issue to raise a ticket.')
    st.code('How do I reset my VPN password?\nWhat is the status of my laptop issue?\nMy printer prints blank pages. Please raise a ticket.',language=None)
for event in st.session_state.events:
    with st.chat_message('user'):
        st.text(event['message'])
    with st.chat_message('assistant'):
        st.text(event['reply'])
        with st.expander('Tool results and workflow'):
            st.write(' → '.join(event['trace']))
            st.json(event['result'])
message = st.chat_input('Describe your IT request',max_chars=2000)
if message:
    with st.spinner('Processing request…'):
        try:
            result = assistant.chat(message)
            st.session_state.events.append({k:result[k] for k in ('message','reply','trace','result')})
            st.session_state.events = st.session_state.events[-20:]
        except Exception as exc:
            logging.getLogger(__name__).warning('request_failure type=%s',type(exc).__name__)
            st.error('The request could not finish. Retry or clear the conversation.')
            st.stop()
    st.rerun()
