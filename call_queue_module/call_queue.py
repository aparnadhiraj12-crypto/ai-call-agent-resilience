# call_queue_module/call_queue.py

from logs.log_manager import log_event


class CallQueue:
    def __init__(self, contacts):
        self.queue = contacts

    def has_next(self):
        return len(self.queue) > 0

    def next_call(self):
        contact = self.queue.pop(0)
        log_event(
            "INFO",
            "CallQueue",
            f"Processing next contact: {contact}"
        )
        return contact

    def skip_contact(self, contact, reason):
        log_event(
            "WARNING",
            "CallQueue",
            f"Skipping contact {contact}: {reason}"
        )
