import logging
import os
from datetime import datetime


class TextLogHandler(logging.Handler):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def emit(self, record):
        log_entry = f"{self.format(record)}\n"

        # Write to file
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(log_entry)


def setup_logger(name="Flow Studio", log_dir=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Generate text file name based on current date
    current_date = datetime.now().strftime("%Y_%m_%d")
    log_file = os.path.join(log_dir, f"log_date{current_date}.txt")

    # Create TextLogHandler
    text_handler = TextLogHandler(log_file)

    # Set log format
    formatter = logging.Formatter('%(message)s')  # Only format the message part
    text_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(text_handler)

    return logger
