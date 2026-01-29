AI Call Agent – Error Recovery & Resilience System
Project Overview

This project simulates an AI Call Agent that interacts with multiple external services (e.g., ElevenLabs TTS, LLMs, CRM APIs).
It is designed with robust error handling, retries, circuit breakers, logging, alerting, and health checks to ensure that service failures do not cascade and the system continues to operate gracefully.

Features

Error Categorization

Differentiates between:

Transient errors (e.g., 503 Service Unavailable, network timeouts)

Permanent errors (e.g., 401 Unauthorized, invalid payload)

Custom exception hierarchy:

TransientServiceError

PermanentServiceError

Retry Logic with Exponential Backoff

Configurable parameters:

Maximum retries

Initial delay

Backoff factor

Retries apply only to transient errors

Retry attempts are logged with retry count and circuit breaker state

Circuit Breaker Pattern

One circuit breaker per external service

Configurable parameters:

Failure threshold

Recovery timeout

States:

Closed: normal operation

Open: fail-fast, requests blocked

Half-Open: testing recovery after timeout

Circuit breaker updates automatically based on success/failure of service calls

Logging & Observability

Logs structured events locally and optionally to Google Sheets

Includes:

Timestamp

Service name

Error category

Retry count

Circuit breaker state

Alerts for Critical Failures

Alerts are triggered for:

Permanent service failures

Circuit breaker opening after repeated transient failures

Supported channels:

Email

Telegram

Webhook (HTTP endpoint)

Health Checks

Background health checker monitors services periodically

Detects recovery and resets circuit breaker when service is healthy

Prevents stale failures from blocking operations indefinitely

Graceful Degradation

If a service is unavailable:

Skips current call

Moves to next contact in the queue

Avoids blocking the entire system

Fallback behavior can be extended for alternate service paths

Architecture
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

Configuration

Retry parameters (config.py or simulate_ai_call_agent.py):

RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay": 5,
    "backoff_factor": 2
}


Circuit breaker parameters:

CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 2,
    "recovery_timeout": 10  # seconds
}


Health check interval:

HEALTH_CHECK_CONFIG = {
    "interval": 5  # seconds
}

Error Flow

A call is sent to a service (e.g., text_to_speech)

If service returns a TransientServiceError:

RetryHandler retries with exponential backoff

Circuit breaker counts failure

Logs retry attempts

If all retries fail:

Alert is triggered

Call is marked failed

Circuit breaker may open if threshold exceeded

If a PermanentServiceError occurs:

Alert is triggered immediately

Circuit breaker records failure

Current call is aborted

Circuit Breaker Behavior
State	Behavior
Closed	Normal operation, requests pass through
Open	Requests blocked, fail-fast, logs warning
Half-Open	Test requests allowed, transitions to Closed on success, Open on fail
Health Check

Runs periodically in a separate thread

Checks if services are healthy

Resets circuit breaker to Closed when service recovers

Ensures system resumes processing pending calls

Logging & Alerts

Logs include:

timestamp

level (INFO, WARNING, ERROR, CRITICAL)

service

message

retry_count

circuit_state

Alerts sent via:

Webhook (generic)

Email (configurable)

Telegram (configurable)

How to Run

Simulation:

python simulate_ai_call_agent.py


Simulates transient failure → retries → circuit breaker → recovery

Production-like run:

python main.py


Uses real service integration (mocked or real)

Example Logs
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

Folder Structure
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