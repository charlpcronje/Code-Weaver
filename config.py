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