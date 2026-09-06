"""SQLite repository with parameterized queries and atomic deduplication."""
import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

def normalize(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))

class Store:
    def __init__(self, path, seed_path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        seed = json.loads(Path(seed_path).read_text(encoding='utf-8'))
        with self.connection() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS employees(id TEXT PRIMARY KEY, name TEXT, department TEXT);
                CREATE TABLE IF NOT EXISTS articles(id TEXT PRIMARY KEY, title TEXT, body TEXT, tags TEXT);
                CREATE TABLE IF NOT EXISTS tickets(
                  id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES employees(id),
                  title TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL,
                  created_at TEXT NOT NULL, fingerprint TEXT NOT NULL);
                CREATE UNIQUE INDEX IF NOT EXISTS active_issue ON tickets(employee_id,fingerprint)
                  WHERE status IN ('Open','In progress');
                CREATE TABLE IF NOT EXISTS audit(
                  id INTEGER PRIMARY KEY, action TEXT NOT NULL, ticket_id TEXT, created_at TEXT NOT NULL);
            ''')
            db.executemany('INSERT OR IGNORE INTO employees VALUES(:id,:name,:department)', seed['employees'])
            db.executemany('INSERT OR IGNORE INTO articles VALUES(:id,:title,:body,:tags)', seed['articles'])
            for ticket in seed['tickets']:
                db.execute('INSERT OR IGNORE INTO tickets VALUES(?,?,?,?,?,?,?)',
                    (ticket['id'], ticket['employee_id'], ticket['title'], ticket['description'],
                     ticket['status'], ticket['created_at'], self.fingerprint(ticket['description'])))

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def fingerprint(description):
        return hashlib.sha256(normalize(description).encode()).hexdigest()

    def employees(self):
        with self.connection() as db:
            return [dict(r) for r in db.execute('SELECT * FROM employees ORDER BY id')]

    def validate_employee(self, employee_id):
        with self.connection() as db:
            if not db.execute('SELECT 1 FROM employees WHERE id=?', (employee_id,)).fetchone():
                raise ValueError('Select a valid employee profile.')

    def search(self, query):
        words = set(normalize(query).split()) - {'how','do','i','my','the','a','is','to','please','what','can','you'}
        with self.connection() as db:
            articles = [dict(r) for r in db.execute('SELECT * FROM articles')]
        ranked = [(len(words & set(normalize(a['title']+' '+a['tags']).split())), a) for a in articles]
        return [a for score,a in sorted(ranked, key=lambda x: -x[0]) if score > 0][:3]

    def lookup(self, employee_id, query=''):
        self.validate_employee(employee_id)
        with self.connection() as db:
            rows = [dict(r) for r in db.execute(
                'SELECT id,title,description,status,created_at FROM tickets WHERE employee_id=? ORDER BY created_at DESC',
                (employee_id,))]
        ids = re.findall(r'IT-[A-Z0-9]+', query.upper())
        if ids:
            return [r for r in rows if r['id'] in ids]
        words = set(normalize(query).split()) & {'vpn','laptop','email','printer','wifi','password','monitor'}
        return [r for r in rows if not words or words & set(normalize(r['title']+' '+r['description']).split())]

    def create(self, employee_id, title, description):
        self.validate_employee(employee_id)
        title, description = title.strip(), description.strip()
        if not 5 <= len(title) <= 120 or not 10 <= len(description) <= 2000:
            raise ValueError('Ticket title needs 5–120 characters and description needs 10–2000 characters.')
        fingerprint = self.fingerprint(description)
        now = datetime.now(timezone.utc).isoformat()
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute("SELECT * FROM tickets WHERE employee_id=? AND fingerprint=? AND status IN ('Open','In progress')",
                                  (employee_id, fingerprint)).fetchone()
            if existing:
                return {'created': False, 'ticket': dict(existing)}
            ticket_id = 'IT-' + uuid.uuid4().hex[:12].upper()
            db.execute('INSERT INTO tickets VALUES(?,?,?,?,?,?,?)',
                       (ticket_id,employee_id,title,description,'Open',now,fingerprint))
            db.execute('INSERT INTO audit(action,ticket_id,created_at) VALUES(?,?,?)',('ticket_created',ticket_id,now))
            row = db.execute('SELECT * FROM tickets WHERE id=?',(ticket_id,)).fetchone()
            return {'created': True, 'ticket': dict(row)}
