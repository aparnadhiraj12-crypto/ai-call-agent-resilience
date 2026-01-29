# config.py

# Retry configuration
RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay": 5,     # seconds
    "backoff_factor": 2
}

# Circuit breaker configuration
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 2,  # default
    "recovery_timeout": 10
}



# Health check configuration
HEALTH_CHECK_CONFIG = {
    "interval": 10  # seconds
}

# Logging configuration
LOG_FILE_PATH = "logs/app.log"
SHEETS_LOG_PATH = "logs/google_sheets_mock.csv"

# Alert thresholds
ALERT_CONFIG = {
    "max_downtime": 30  # seconds
}
EMAIL_ENABLED = False
TELEGRAM_ENABLED = False
WEBHOOK_ENABLED = True   # Enable this for demo screenshots

