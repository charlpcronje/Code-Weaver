#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import Config
from file_monitor import FileMonitor
from content_parser import ContentParser
from git_operations import GitOperations
from backup_system import BackupSystem

class Weaver:
    def __init__(self):
        self.config = Config()
        self.setup_logging()
        self.file_monitor = FileMonitor(self.config.monitored_file, self.process_file)
        self.content_parser = ContentParser()
        self.git_ops = GitOperations(self.config.project_root)
        self.backup_system = BackupSystem(self.config.backups_folder)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.config.logs_folder, 'weaver.log')),
                logging.StreamHandler()
            ]
        )

    def process_file(self, file_path):
        logging.info(f"Change detected in {file_path}")
        with open(file_path, 'r') as file:
            content = file.read()
        
        if not content.strip():
            logging.info("File is empty. Skipping processing.")
            return

        updates = self.content_parser.parse(content)
        branch_name = self.git_ops.create_update_branch()

        for file_path, file_content in updates:
            normalized_path = os.path.join(self.config.project_root, file_path)
            if os.path.exists(normalized_path):
                self.backup_system.create_backup(normalized_path)
            
            os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
            with open(normalized_path, 'w') as file:
                file.write(file_content)
            
            self.git_ops.stage_file(file_path)

        merge_result = self.git_ops.merge_branch(branch_name)
        if not merge_result:
            logging.warning("Merge conflicts detected. Opening VS Code for resolution.")
            self.open_vscode_for_merge()

        self.generate_log(updates, branch_name, merge_result)
        self.clear_monitored_file()

    def open_vscode_for_merge(self):
        os.system(f"code-server --goto {self.config.project_root}")

    def generate_log(self, updates, branch_name, merge_result):
        log_content = f"""
        Update Summary:
        - Files processed: {len(updates)}
        - Files added/updated: {len(updates)}
        - Branch created: {branch_name}
        - Merge status: {"Automatic" if merge_result else "Manual intervention required"}

        Updated files:
        {chr(10).join(f"- {file_path}" for file_path, _ in updates)}
        """
        log_file = os.path.join(self.config.logs_folder, f"update_{branch_name}.log")
        with open(log_file, 'w') as file:
            file.write(log_content)

    def clear_monitored_file(self):
        with open(self.config.monitored_file, 'w') as file:
            file.write('')

    def run(self):
        self.file_monitor.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.file_monitor.stop()

if __name__ == "__main__":
    weaver = Weaver()
    weaver.run()