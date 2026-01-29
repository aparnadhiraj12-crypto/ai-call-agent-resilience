# logs/logger.py

import json
import os
import threading
from datetime import datetime
from config import LOG_FILE_PATH

_lock = threading.Lock()

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)


def log(level, service, message, retry_count=None, circuit_state=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": service,
        "message": message,
        "retry_count": retry_count,
        "circuit_state": circuit_state
    }

    # Console output
    print(json.dumps(log_entry, indent=2))

    # File output (thread-safe)
    try:
        with _lock:
            with open(LOG_FILE_PATH, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print("⚠ Logging failed:", e)

    return log_entry
