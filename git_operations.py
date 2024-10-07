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