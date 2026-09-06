"""Repeatable live demonstration with a temporary database, no API key needed."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ops_assistant.agent import Assistant
from ops_assistant.router import DemoRouter
from ops_assistant.store import Store

def main():
    with tempfile.TemporaryDirectory() as temp:
        store = Store(Path(temp)/'demo.db',Path(__file__).resolve().parents[1]/'data/seed.json')
        agent = Assistant(store,DemoRouter(),'EMP1024')
        for text in ['How do I reset my VPN password?', 'What is the status of my laptop issue?',
                     'Please raise a ticket','My printer prints blank pages','confirm',
                     'My printer prints blank pages. Please raise a ticket.','confirm']:
            result = agent.chat(text)
            print('\nUSER:',text,'\nASSISTANT:',result['reply'],'\nWORKFLOW:', ' -> '.join(result['trace']))

if __name__ == '__main__':
    main()
