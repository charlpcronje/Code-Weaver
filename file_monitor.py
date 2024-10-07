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