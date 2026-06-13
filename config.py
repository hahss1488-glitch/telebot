from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    backup_dir: Path = BASE_DIR / "backups"
    log_dir: Path = BASE_DIR / "logs"
    data_dir: Path = BASE_DIR / "data"
    log_level: str = "INFO"

    @property
    def sqlite_path(self) -> Path:
        if self.database_url.startswith("sqlite+aiosqlite:///"):
            return BASE_DIR / self.database_url.replace("sqlite+aiosqlite:///", "", 1)
        if self.database_url.startswith("sqlite:///"):
            return BASE_DIR / self.database_url.replace("sqlite:///", "", 1)
        return self.data_dir / "telebot.db"


def load_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")
    settings = Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/telebot.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    settings.backup_dir.mkdir(parents=True, exist_ok=True)
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
