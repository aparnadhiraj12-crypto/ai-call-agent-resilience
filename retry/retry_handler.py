import time
from errors.exceptions import TransientServiceError
from logs.log_manager import log_event


class RetryHandler:
    def __init__(self, max_retries=3, initial_delay=5, backoff_factor=2):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor

    def execute(self, func, circuit_breaker=None, *args, **kwargs):
        """
        Executes a function with retries for transient errors and interacts with a circuit breaker.

        Parameters:
        - func: The function to execute
        - circuit_breaker: CircuitBreaker object to record success/failure
        - *args, **kwargs: Arguments to forward to func
        """

        delay = self.initial_delay

        # Try to get service name for logging
        service_name = getattr(func.__self__, '__class__', None)
        if service_name:
            service_name = service_name.__name__
        else:
            service_name = "Service"

        for attempt in range(1, self.max_retries + 1):
            try:
                # Only forward *args intended for the actual service function
                result = func(*args, **kwargs)

                # Record success in circuit breaker if provided
                if circuit_breaker:
                    circuit_breaker.record_success()

                return result

            except TransientServiceError as e:
                log_event(
                    "WARNING",
                    service_name,
                    f"Retry {attempt}/{self.max_retries} failed: {str(e)}. Retrying in {delay}s",
                    retry_count=attempt,
                    circuit_state=circuit_breaker.state.value if circuit_breaker else None
                )

                if attempt == self.max_retries:
                    log_event(
                        "ERROR",
                        service_name,
                        "All retries exhausted. Raising error.",
                        retry_count=attempt,
                        circuit_state=circuit_breaker.state.value if circuit_breaker else None
                    )

                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    raise

                time.sleep(delay)
                delay *= self.backoff_factor
