import os
import shutil
from datetime import datetime

class BackupSystem:
    def __init__(self, backup_folder):
        self.backup_folder = backup_folder

    def create_backup(self, file_path):
        relative_path = os.path.relpath(file_path, start=os.getcwd())
        backup_path = os.path.join(self.backup_folder, relative_path)
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        filename, ext = os.path.splitext(backup_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_backup_path = f"{filename}-{timestamp}{ext}"

        shutil.copy2(file_path, new_backup_path)