"""Validated environment configuration. Secrets never enter graph state."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class Settings:
    mode: str
    database: Path
    model: str
    api_key: str

    @classmethod
    def load(cls):
        load_dotenv(ROOT / '.env')
        mode = os.getenv('ASSISTANT_MODE', 'demo').lower()
        if mode not in {'demo', 'llm'}:
            raise ValueError('ASSISTANT_MODE must be demo or llm.')
        key = os.getenv('OPENAI_API_KEY', '')
        if mode == 'llm' and not key:
            raise ValueError('Set OPENAI_API_KEY in .env to use llm mode.')
        path = Path(os.getenv('DATABASE_PATH', 'runtime/support.db'))
        return cls(mode, path if path.is_absolute() else ROOT / path,
                   os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'), key)
