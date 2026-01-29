# errors/exceptions.py

class BaseServiceError(Exception):
    """Base class for all service errors"""
    def __init__(self, message, service_name=None):
        super().__init__(message)
        self.service_name = service_name


class TransientServiceError(BaseServiceError):
    """Errors that can be retried (timeouts, temporary failures)"""
    pass


class PermanentServiceError(BaseServiceError):
    """Errors that should NOT be retried (auth, invalid request)"""
    pass
