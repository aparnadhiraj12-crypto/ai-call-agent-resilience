import threading
import time

from services.elevenlabs_mock import ElevenLabsService
from retry.retry_handler import RetryHandler
from circuit_breaker.circuit_breaker import CircuitBreaker
from alerts.alert_manager import send_alert
from logs.logger import log
from logs.sheets_logger import log_to_sheets
from errors.exceptions import TransientServiceError, PermanentServiceError
from call_queue_module.call_queue import CallQueue  
from health.health_check import HealthChecker
from config import RETRY_CONFIG, CIRCUIT_BREAKER_CONFIG


def main():
    # Initialize service
    elevenlabs = ElevenLabsService()

    # Initialize retry handler
    retry_handler = RetryHandler(
        max_retries=RETRY_CONFIG["max_retries"],
        initial_delay=RETRY_CONFIG["initial_delay"],
        backoff_factor=RETRY_CONFIG["backoff_factor"]
    )

    # Initialize circuit breaker
    circuit_breaker = CircuitBreaker(
        service_name="ElevenLabs",
        failure_threshold=CIRCUIT_BREAKER_CONFIG["failure_threshold"],
        recovery_timeout=CIRCUIT_BREAKER_CONFIG["recovery_timeout"]
    )

    # Call queue (graceful degradation)
    call_queue = CallQueue([
        "Contact-1",
        "Contact-2",
        "Contact-3",
        "Contact-4"
    ])

    # Start health checker in background
    health_checker = HealthChecker("ElevenLabs", elevenlabs, circuit_breaker)
    threading.Thread(target=health_checker.start, daemon=True).start()

    # Process calls
    while call_queue.has_next():
        contact = call_queue.next_call()
        log("INFO", "System", f"Processing call for {contact}")

        if not circuit_breaker.allow_request():
            log(
                "WARNING",
                "ElevenLabs",
                "Circuit OPEN. Skipping call.",
                circuit_state=circuit_breaker.state.value
            )
            continue

        try:
            # ✅ Corrected: pass only the arguments intended for text_to_speech
            retry_handler.execute(
                elevenlabs.text_to_speech,  # method
                circuit_breaker,            # CircuitBreaker object
                f"Hello {contact}"          # forwarded to text_to_speech(text)
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
        elevenlabs.fail_mode = False


if __name__ == "__main__":
    main()
