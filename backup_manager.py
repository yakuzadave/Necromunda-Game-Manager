import os
import shutil
import json
from datetime import datetime
import streamlit as st
from utils.logger import log_info, log_error, log_debug

class BackupManager:
    """Manages backups of game data"""
    
    def __init__(self):
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup(self):
        """Create a backup of the current game data"""
        try:
            # Timestamp for the backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create a timestamped backup directory
            backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup data files
            data_files = ["campaign_data.json", "full_campaign_data.json"]
            for file in data_files:
                if os.path.exists(file):
                    shutil.copy2(file, os.path.join(backup_path, file))
                    log_debug(f"Backed up {file}")
            
            # Backup data directories
            data_dirs = ["data/gangs", "data/territories", "data/battles", "data/equipment"]
            for directory in data_dirs:
                if os.path.exists(directory):
                    backup_subdir = os.path.join(backup_path, directory)
                    os.makedirs(os.path.dirname(backup_subdir), exist_ok=True)
                    if os.path.exists(directory):
                        shutil.copytree(directory, backup_subdir, dirs_exist_ok=True)
                        log_debug(f"Backed up directory {directory}")
            
            # Create a metadata file
            metadata = {
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "files_backed_up": data_files,
                "directories_backed_up": data_dirs
            }
            
            with open(os.path.join(backup_path, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=4)
                
            log_info(f"Backup created at {backup_path}")
            return backup_path
            
        except Exception as e:
            log_error(f"Backup creation failed: {e}", exc_info=True)
            return None
    
    def restore_backup(self, backup_timestamp=None):
        """
        Restore a backup. If no timestamp is provided, 
        restore the most recent backup.
        """
        try:
            # List available backups
            backups = sorted([d for d in os.listdir(self.backup_dir) 
                             if d.startswith("backup_")])
            
            if not backups:
                log_error("No backups available to restore")
                return False
            
            # Select the backup to restore
            if backup_timestamp:
                backup_dir = f"backup_{backup_timestamp}"
                if backup_dir not in backups:
                    log_error(f"Backup {backup_dir} not found")
                    return False
            else:
                # Default to the most recent
                backup_dir = backups[-1]
            
            backup_path = os.path.join(self.backup_dir, backup_dir)
            
            # Check metadata
            metadata_path = os.path.join(backup_path, "metadata.json")
            if not os.path.exists(metadata_path):
                log_error(f"Backup metadata not found at {metadata_path}")
                return False
                
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                
            # Restore data files
            for file in metadata.get("files_backed_up", []):
                source = os.path.join(backup_path, file)
                if os.path.exists(source):
                    shutil.copy2(source, file)
                    log_debug(f"Restored {file}")
            
            # Restore directories
            for directory in metadata.get("directories_backed_up", []):
                source = os.path.join(backup_path, directory)
                if os.path.exists(source):
                    if os.path.exists(directory):
                        shutil.rmtree(directory)
                    parent_dir = os.path.dirname(directory)
                    if parent_dir and not os.path.exists(parent_dir):
                        os.makedirs(parent_dir, exist_ok=True)
                    shutil.copytree(source, directory)
                    log_debug(f"Restored directory {directory}")
            
            log_info(f"Restored backup from {metadata.get('datetime')}")
            return True
            
        except Exception as e:
            log_error(f"Backup restoration failed: {e}", exc_info=True)
            return False
    
    def list_backups(self):
        """List all available backups with timestamps"""
        backups = []
        for backup_dir in sorted(os.listdir(self.backup_dir)):
            if (backup_dir.startswith("backup_")):
                metadata_path = os.path.join(self.backup_dir, backup_dir, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    backups.append(metadata)
        return backups
