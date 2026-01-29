# health/health_check.py

import time
from config import HEALTH_CHECK_CONFIG
from logs.log_manager import log_event


class HealthChecker:
    def __init__(self, service_name, service, circuit_breaker):
        self.service_name = service_name
        self.service = service
        self.circuit_breaker = circuit_breaker

    def start(self):
        while True:
            time.sleep(HEALTH_CHECK_CONFIG["interval"])

            if not getattr(self.service, "fail_mode", False):
                if self.circuit_breaker.state != self.circuit_breaker.state.CLOSED:
                    self.circuit_breaker.record_success()

                    log_event(
                        "INFO",
                        self.service_name,
                        "Health check successful. Circuit reset.",
                        circuit_state=self.circuit_breaker.state.value
                    )
