# health/health_monitor.py

import time
from config import HEALTH_CHECK_CONFIG, ALERT_CONFIG
from logs.log_manager import log_event
from alerts.alert_manager import send_alert


class HealthMonitor:
    def __init__(self, service_name, circuit_breaker, service):
        self.service_name = service_name
        self.circuit_breaker = circuit_breaker
        self.service = service
        self.last_alert_time = 0

    def run(self):
        while True:
            time.sleep(HEALTH_CHECK_CONFIG["interval"])

            # 🔁 Service recovered
            if not self.service.fail_mode:
                if self.circuit_breaker.state != self.circuit_breaker.state.CLOSED:
                    self.circuit_breaker.record_success()

                    log_event(
                        "INFO",
                        self.service_name,
                        "Health monitor detected recovery",
                        circuit_state=self.circuit_breaker.state.value
                    )
                continue

            # 🚨 Service still unhealthy → long downtime alert
            if self.circuit_breaker.state == self.circuit_breaker.state.OPEN:
                now = time.time()

                if now - self.last_alert_time > ALERT_CONFIG["max_downtime"]:
                    send_alert(
                        self.service_name,
                        "Service remains down beyond acceptable threshold"
                    )

                    log_event(
                        "CRITICAL",
                        self.service_name,
                        "Dependency downtime exceeded threshold",
                        circuit_state=self.circuit_breaker.state.value
                    )

                    self.last_alert_time = now
