from logs.logger import log
from logs.sheets_logger import log_to_sheets

def log_event(level, service, message, retry_count=None, circuit_state=None):
    log(level, service, message, retry_count, circuit_state)
    log_to_sheets(level, service, message, retry_count, circuit_state)
