
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self, data_dir="data"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        try:
            # Create a new backup directory with timestamp
            shutil.copytree(data_dir, backup_path)
            
            # Keep only the last 5 backups
            self._cleanup_old_backups()
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
            
    def _cleanup_old_backups(self, keep_last=5):
        backups = sorted(self.backup_dir.glob("backup_*"))
        if len(backups) > keep_last:
            for backup in backups[:-keep_last]:
                shutil.rmtree(backup)
