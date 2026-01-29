##AI Call Agent – Error Recovery & Resilience System##

A robust AI Call Agent simulation with advanced error handling, retry mechanisms, circuit breaker patterns, logging, alerting, and health checks.
Ensures that failures in external services (e.g., ElevenLabs TTS, LLMs, CRM APIs) do not block the system.

##🚀 Features##

-Error Categorization – Differentiates between Transient and Permanent errors using a custom exception hierarchy:
TransientServiceError, PermanentServiceError

-Retry Logic with Exponential Backoff – Configurable max_retries, initial_delay, backoff_factor. Retries apply only for transient errors

-Circuit Breaker Pattern – Tracks failures per service with Closed, Open, and Half-Open states. Configurable failure threshold and recovery timeout

-Logging & Observability – Structured logs with timestamp, service, error type, retry count, and circuit state. Supports logging to Google Sheets

-Alerts for Critical Failures – Sends alerts via Webhook, Email, and Telegram for permanent failures or circuit breaker openings

-Health Checks – Periodic background checks on service health, resets circuit breaker when service recovers

-Graceful Degradation – Skips failed calls and continues processing the next contact, avoiding full system blockage

##🛠️ Tech Stack##

-Language: Python 3.11+

-Framework: Flask 

-Logging: Google Sheets API

-Other Modules: Threading, Requests, etc.

##⚙️ Configuration##
# Retry configuration
```
RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay": 5,
    "backoff_factor": 2
}

# Circuit breaker configuration
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 2,
    "recovery_timeout": 10  # seconds
}

# Health check interval
HEALTH_CHECK_CONFIG = {
    "interval": 5  # seconds
}
```
##🏗️ Architecture ##
```
+-------------------------+
| Call Queue              |
| - Holds pending calls   |
+-------------------------+
           |
           v
+-------------------------+
| RetryHandler            |
| - Executes service calls|
| - Applies exponential   |
|   backoff on transient  |
|   errors                |
+-------------------------+
           |
           v
+-------------------------+
| CircuitBreaker          |
| - Tracks failures       |
| - Blocks requests if    |
|   service is unhealthy  |
+-------------------------+
           |
           v
+-------------------------+
| External Services       |
| (e.g., ElevenLabs TTS) |
+-------------------------+
           ^
           |
+-------------------------+
| HealthChecker           |
| - Periodically checks   |
|   service health        |
| - Resets circuit breaker|
+-------------------------+
```

##📜 Error Flow ##

-Transient Error → RetryHandler retries with exponential backoff
Circuit breaker counts failure, logs retry attempts, triggers alert if retries fail

-Permanent Error → Alert triggered immediately, current call aborted, circuit breaker records failure

##📈 Logging & Alerts ##

-Logs structured events locally and optionally to Google Sheets

-Includes: timestamp, level, service, message, retry_count, circuit_state

-Alerts triggered via: Webhook, Email, Telegram

Example Logs:
```

{
  "timestamp": "2026-01-29T18:17:19",
  "level": "ERROR",
  "service": "ElevenLabs",
  "message": "503 Service Unavailable",
  "retry_count": 3,
  "circuit_state": "CLOSED"
}
{
  "timestamp": "2026-01-29T18:17:25",
  "level": "WARNING",
  "service": "ElevenLabs",
  "message": "Circuit OPEN. Skipping call.",
  "retry_count": null,
  "circuit_state": "OPEN"
}
{
  "timestamp": "2026-01-29T18:17:35",
  "level": "INFO",
  "service": "ElevenLabs",
  "message": "Call successful for Contact-1",
  "retry_count": 1,
  "circuit_state": "CLOSED"
}
```

##▶️ How to Run ##
# Simulation mode
```
python simulate_ai_call_agent.py
```
# Simulates transient failures → retries → circuit breaker → recovery

# Production-like run
```
python main.py
```
# Uses real or mocked service integrations

##📁 Project Structure ##
```
ai-call-agent-resilience/
├── main.py
├── simulate_ai_call_agent.py
├── config.py
├── retry/
│   └── retry_handler.py
├── circuit_breaker/
│   └── circuit_breaker.py
├── health/
│   └── health_check.py
├── alerts/
│   └── alert_manager.py
├── logs/
│   ├── logger.py
│   ├── log_manager.py
│   └── sheets_logger.py
├── services/
│   └── elevenlabs_mock.py
├── call_queue_module/
│   └── call_queue.py
└── errors/
    └── exceptions.py
```

##⚙️ How It Works ##

-Call Queue – Holds pending contacts

-RetryHandler – Executes service calls; retries transient failures with exponential backoff

-CircuitBreaker – Opens after repeated failures, blocks requests, half-opens after recovery timeout

-HealthChecker – Monitors service health; resets circuit breaker when service recovers

-Alerts – Sends notifications on permanent failures or circuit breaker opening

