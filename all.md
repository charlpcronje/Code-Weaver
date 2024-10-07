###FILE_START:weaver.py###
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
###FILE_END:weaver.py###

###FILE_START:config.py###
import os
import json
from pathlib import Path

class Config:
    def __init__(self):
        self.config_file = os.path.join(os.getcwd(), '.weaver', 'config.json')
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.create_default_config()
        
        with open(self.config_file, 'r') as file:
            config = json.load(file)
        
        self.project_root = config.get('project_root', os.getcwd())
        self.logs_folder = config.get('logs_folder', os.path.join(self.project_root, '.weaver', 'logs'))
        self.backups_folder = config.get('backups_folder', os.path.join(self.project_root, '.weaver', 'backups'))
        self.monitored_file = config.get('monitored_file', os.path.join(self.project_root, 'weaver.md'))

    def create_default_config(self):
        default_config = {
            'project_root': os.getcwd(),
            'logs_folder': os.path.join(os.getcwd(), '.weaver', 'logs'),
            'backups_folder': os.path.join(os.getcwd(), '.weaver', 'backups'),
            'monitored_file': os.path.join(os.getcwd(), 'weaver.md')
        }

        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as file:
            json.dump(default_config, file, indent=4)

        print("Default configuration created. Please review and modify if needed.")
###FILE_END:config.py###

###FILE_START:file_monitor.py###
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class FileMonitor:
    def __init__(self, file_path, callback):
        self.file_path = file_path
        self.callback = callback
        self.observer = Observer()

    def start(self):
        event_handler = FileChangeHandler(self.callback)
        self.observer.schedule(event_handler, path=self.file_path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)
###FILE_END:file_monitor.py###

###FILE_START:content_parser.py###
import re

class ContentParser:
    def parse(self, content):
        updates = []
        current_file = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('###FILE_START:'):
                if current_file:
                    updates.append((current_file, '\n'.join(current_content)))
                current_file = line[14:-3]
                current_content = []
            elif line.startswith('###FILE_END:'):
                if current_file:
                    updates.append((current_file, '\n'.join(current_content)))
                current_file = None
                current_content = []
            elif current_file:
                current_content.append(line)

        return updates
###FILE_END:content_parser.py###

###FILE_START:git_operations.py###
import git
import os
from datetime import datetime

class GitOperations:
    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)

    def create_update_branch(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        branch_name = f"ai-update-{timestamp}"
        self.repo.git.checkout('-b', branch_name)
        return branch_name

    def stage_file(self, file_path):
        self.repo.index.add([file_path])

    def merge_branch(self, branch_name):
        try:
            self.repo.git.checkout('main')
            self.repo.git.merge(branch_name)
            return True
        except git.GitCommandError:
            return False
###FILE_END:git_operations.py###

###FILE_START:backup_system.py###
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
###FILE_END:backup_system.py###

###FILE_START:.weaver/prompt.md###
# Instructions for AI Response Formatting

When providing responses that include file updates or creations, please use the following format:

###FILE_START:path/to/file.ext###
Content of the file goes here.
Make sure to include all necessary code or text without any omissions.
Do not use placeholders or ellipsis (...) to indicate omitted content.
###FILE_END:path/to/file.ext###

###FILE_START:another/file.py###
def example_function():
    print("This is an example")
###FILE_END:another/file.py###

You can include multiple files in a single response.
Each file should start with "###FILE_START:" followed by the relative path and end with "###FILE_END:" followed by the same relative path.
Ensure that the entire content of each file is included between these markers.
###FILE_END:.weaver/prompt.md###

###FILE_START:setup.py###
from setuptools import setup, find_packages

setup(
    name='codeweaver',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'watchdog',
        'gitpython',
    ],
    entry_points={
        'console_scripts': [
            'weaver=weaver:main',
        ],
    },
)
###FILE_END:setup.py###

###FILE_START:README.md###
# CodeWeaver

CodeWeaver is a Python application designed to automate file updates based on AI responses. It monitors a specific file for changes, processes the content, and updates project files accordingly using Git for version control.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/codeweaver.git
   ```

2. Navigate to the project directory:
   ```
   cd codeweaver
   ```

3. Install the package:
   ```
   pip install -e .
   ```

## Usage

1. Run the CodeWeaver application:
   ```
   weaver
   ```

2. The application will create a default configuration if one doesn't exist. Review and modify the `.weaver/config.json` file if needed.

3. Edit the `weaver.md` file in your project root to add or update files. The application will automatically detect changes and process them.

4. CodeWeaver will create Git branches, stage changes, and attempt to merge them automatically. If conflicts occur, it will open VS Code (code-server) for manual resolution.

5. Check the logs in the `.weaver/logs` directory for detailed information about each update process.

## Configuration

The `.weaver/config.json` file contains the following settings:

- `project_root`: The root directory of your project
- `logs_folder`: Directory for storing log files
- `backups_folder`: Directory for storing file backups
- `monitored_file`: The file to monitor for changes (default: `weaver.md`)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
###FILE_END:README.md###