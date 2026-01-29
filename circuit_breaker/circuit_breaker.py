import time
from enum import Enum
from logs.log_manager import log_event
from alerts.alert_manager import send_alert


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, service_name, failure_threshold=3, recovery_timeout=15):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def allow_request(self):
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - (self.last_failure_time or 0)
            if elapsed >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                log_event(
                    "INFO",
                    self.service_name,
                    "Circuit breaker HALF_OPEN — testing service",
                    circuit_state=self.state.value
                )
                return True
            return False
        return True

    def record_success(self):
        previous = self.state
        self.failure_count = 0
        self.state = CircuitState.CLOSED

        if previous != CircuitState.CLOSED:
            log_event(
                "INFO",
                self.service_name,
                "Circuit breaker CLOSED — service recovered",
                circuit_state=self.state.value
            )

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        log_event(
            "WARNING",
            self.service_name,
            f"Failure recorded ({self.failure_count}/{self.failure_threshold})",
            circuit_state=self.state.value
        )

        if self.failure_count >= self.failure_threshold and self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN

            log_event(
                "CRITICAL",
                self.service_name,
                "Circuit breaker OPEN — service marked unhealthy",
                circuit_state=self.state.value
            )

            send_alert(
                self.service_name,
                "Circuit breaker OPEN — service unhealthy"
            )
