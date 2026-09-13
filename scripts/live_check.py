"""Opt-in OpenRouter acceptance check. Uses fictional inputs and a temporary DB.

Run with: python scripts/live_check.py
Requires OPENROUTER_API_KEY in .env or the environment. Makes paid model calls.
Never prints credentials, HTTP response bodies or raw exceptions.
"""
import json
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ops_assistant.agent import Assistant
from ops_assistant.config import Settings, ROOT
from ops_assistant.router import LLMRouter
from ops_assistant.store import Store

def main():
    settings = replace(Settings.load(),mode='llm')
    if not settings.api_key:
        print('OPENROUTER_API_KEY is missing. Add it to the local .env first.')
        return 2
    records = []
    with tempfile.TemporaryDirectory() as temp:
        store = Store(Path(temp)/'live.db',ROOT/'data/seed.json')
        router = LLMRouter(settings)
        agent = Assistant(store,router,'EMP1024')
        cases = [
            ('knowledge','How do I reset my VPN password?',lambda s:'KB001' in s['reply']),
            ('lookup','What is the status of my laptop issue?',lambda s:'IT-1001' in s['reply']),
            ('missing_information','Please raise a ticket',lambda s:s.get('pending')=='ticket_creation'),
            ('draft','My printer prints blank pages',lambda s:bool(s.get('draft'))),
            ('confirmed_creation','confirm',lambda s:s.get('result',{}).get('created') is True),
        ]
        try:
            for name,message,check in cases:
                state = agent.chat(message)
                ok = check(state)
                records.append({'case':name,'passed':ok,'trace':state['trace'],'reply':state['reply']})
                if not ok:
                    break
        finally:
            router.client.close()
    report = {'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'provider':'OpenRouter',
              'model':settings.model,'passed':len(records)==len(cases) and all(r['passed'] for r in records),
              'checks':records}
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
