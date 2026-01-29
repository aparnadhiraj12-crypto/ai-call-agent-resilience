import threading
import time
from errors.exceptions import TransientServiceError, PermanentServiceError
from retry.retry_handler import RetryHandler
from circuit_breaker.circuit_breaker import CircuitBreaker
from health.health_check import HealthChecker
from alerts.alert_manager import send_alert
from logs.logger import log
from logs.sheets_logger import log_to_sheets


# -------------------------
# Mock ElevenLabs service
# -------------------------
class MockElevenLabsService:
    def __init__(self):
        self.fail_mode = True  # Start with failure to simulate 503

    def text_to_speech(self, text):
        if self.fail_mode:
            raise TransientServiceError("503 Service Unavailable", service_name="ElevenLabs")
        return f"Audio({text})"


# -------------------------
# Configuration
# -------------------------
RETRY_CONFIG = {
    "max_retries": 3,
    "initial_delay": 5,
    "backoff_factor": 2
}

CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 2,
    "recovery_timeout": 10  # seconds
}

HEALTH_CHECK_CONFIG = {
    "interval": 5  # seconds
}


# -------------------------
# Call Queue
# -------------------------
class CallQueue:
    def __init__(self, contacts):
        self.contacts = contacts
        self.index = 0

    def has_next(self):
        return self.index < len(self.contacts)

    def next_call(self):
        contact = self.contacts[self.index]
        self.index += 1
        return contact


# -------------------------
# Main simulation
# -------------------------
def main():
    elevenlabs = MockElevenLabsService()
    retry_handler = RetryHandler(**RETRY_CONFIG)
    circuit_breaker = CircuitBreaker("ElevenLabs", **CIRCUIT_BREAKER_CONFIG)
    call_queue = CallQueue(["Contact-1", "Contact-2", "Contact-3"])

    # Start health checker in background
    health_checker = HealthChecker("ElevenLabs", elevenlabs, circuit_breaker)
    threading.Thread(target=health_checker.start, daemon=True).start()

    while call_queue.has_next():
        contact = call_queue.next_call()
        log("INFO", "System", f"Processing call for {contact}")

        # Skip call if circuit breaker is open
        if not circuit_breaker.allow_request():
            log(
                "WARNING",
                "ElevenLabs",
                "Circuit OPEN. Skipping call.",
                circuit_state=circuit_breaker.state.value
            )
            continue

        try:
            # ✅ Corrected execute call
            retry_handler.execute(
                elevenlabs.text_to_speech,  # method
                circuit_breaker,            # circuit breaker object
                f"Hello {contact}"          # text argument
            )

            log(
                "INFO",
                "ElevenLabs",
                f"Call successful for {contact}",
                circuit_state=circuit_breaker.state.value
            )

        except TransientServiceError as e:
            log(
                "ERROR",
                "ElevenLabs",
                str(e),
                retry_count=RETRY_CONFIG["max_retries"],
                circuit_state=circuit_breaker.state.value
            )
            log_to_sheets("ElevenLabs", "Transient", str(e))
            send_alert("ElevenLabs", "Transient failure, retries exhausted")
            circuit_breaker.record_failure()

        except PermanentServiceError as e:
            log(
                "CRITICAL",
                "ElevenLabs",
                str(e),
                circuit_state=circuit_breaker.state.value
            )
            log_to_sheets("ElevenLabs", "Permanent", str(e))
            send_alert("ElevenLabs", "Permanent failure detected")
            break

        # Simulate service recovery after some time
        time.sleep(2)
        elevenlabs.fail_mode = False  # Service becomes healthy


if __name__ == "__main__":
    main()
