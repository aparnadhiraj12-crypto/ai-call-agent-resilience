# logs/sheets_logger.py

import csv
import os
import threading
from datetime import datetime
from config import SHEETS_LOG_PATH

_lock = threading.Lock()

os.makedirs(os.path.dirname(SHEETS_LOG_PATH), exist_ok=True)


def log_to_sheets(level, service, message, retry_count=None, circuit_state=None):
    """
    CSV-based Google Sheets simulation logger
    """
    file_exists = os.path.exists(SHEETS_LOG_PATH)

    with _lock:
        with open(SHEETS_LOG_PATH, "a", newline="") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "timestamp",
                    "level",
                    "service",
                    "message",
                    "retry_count",
                    "circuit_state"
                ])

            writer.writerow([
                datetime.utcnow().isoformat(),
                level,
                service,
                message,
                retry_count,
                circuit_state
            ])
