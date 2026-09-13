"""Validated environment configuration. Secrets never enter graph state."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class Settings:
    mode: str
    database: Path
    model: str
    api_key: str = field(repr=False)
    base_url: str = 'https://openrouter.ai/api/v1'

    @classmethod
    def load(cls):
        load_dotenv(ROOT / '.env')
        mode = os.getenv('ASSISTANT_MODE', 'demo').lower()
        if mode not in {'demo', 'llm'}:
            raise ValueError('ASSISTANT_MODE must be demo or llm.')
        key = os.getenv('OPENROUTER_API_KEY', '').strip()
        if mode == 'llm' and not key:
            raise ValueError('Set OPENROUTER_API_KEY in .env to use llm mode.')
        model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4.1-mini').strip()
        if not model or '/' not in model or any(c.isspace() for c in model):
            raise ValueError('OPENROUTER_MODEL must be a provider/model slug, for example openai/gpt-4.1-mini.')
        path = Path(os.getenv('DATABASE_PATH', 'runtime/support.db'))
        return cls(mode, path if path.is_absolute() else ROOT / path,
                   model, key)
