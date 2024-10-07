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