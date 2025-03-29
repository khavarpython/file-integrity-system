import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import getpass
import os

class CustomLoggingEventHandler(FileSystemEventHandler):
    def __init__(self, log_file, user):
        super().__init__()
        self.log_file = os.path.abspath(log_file)
        self.user = user

    def should_ignore(self, path):
        return os.path.abspath(path) == self.log_file

    def on_created(self, event):
        if self.should_ignore(event.src_path):
            return
        logging.info(f"Created {'directory' if event.is_directory else 'file'}: {event.src_path} - userid:{self.user}")

    def on_modified(self, event):
        if self.should_ignore(event.src_path):
            return
        logging.info(f"Modified {'directory' if event.is_directory else 'file'}: {event.src_path} - userid:{self.user}")

    def on_deleted(self, event):
        if self.should_ignore(event.src_path):
            return
        logging.info(f"Deleted {'directory' if event.is_directory else 'file'}: {event.src_path} - userid:{self.user}")

    def on_moved(self, event):
        if self.should_ignore(event.src_path) or self.should_ignore(event.dest_path):
            return
        logging.info(
            f"Renamed {'directory' if event.is_directory else 'file'}: to {os.path.basename(event.dest_path)} - userid:{self.user}"
        )

if __name__ == '__main__':
    user = getpass.getuser()
    log_file = 'FIM_Logs.log'

    logging.basicConfig(
        filename=log_file,
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s - %(process)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Directory to monitor
    path = r'C:\Users\Briana\Documents\Year 3 Semester 2\Computer Security\SafeBankLtd'

    event_handler = CustomLoggingEventHandler(log_file, user)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
