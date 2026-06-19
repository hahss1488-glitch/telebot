from __future__ import annotations
import logging, shutil
from datetime import datetime
from pathlib import Path
logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self, db_path: Path, backup_dir: Path, keep: int = 5) -> None:
        self.db_path, self.backup_dir, self.keep = db_path, backup_dir, keep
    def create_backup(self) -> Path | None:
        if not self.db_path.exists(): return None
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        target = self.backup_dir / f"backup_{datetime.now():%Y_%m_%d_%H_%M}.db"
        shutil.copy2(self.db_path, target)
        backups = sorted(self.backup_dir.glob("backup_*.db"), reverse=True)
        for old in backups[self.keep:]: old.unlink(missing_ok=True)
        logger.info("Backup created: %s", target)
        return target
