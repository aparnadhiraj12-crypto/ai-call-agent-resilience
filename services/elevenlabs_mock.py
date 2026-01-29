# services/elevenlabs_mock.py

import random
from errors.exceptions import TransientServiceError, PermanentServiceError


class ElevenLabsService:
    def __init__(self):
        self.fail_mode = True   
        self.force_error = None  

    def text_to_speech(self, text):
        """
        Simulates a call to ElevenLabs TTS.
        Can simulate transient failures, permanent failures, or succeed.
        """

        if text == "PERMANENT_FAIL":
            raise PermanentServiceError(
                "ElevenLabs authentication failed",
                service_name="ElevenLabs"
            )

        
        if self.fail_mode:
           
            error_type = self.force_error or random.choice(["timeout", "server", "auth"])

            if error_type == "timeout":
                raise TransientServiceError(
                    "ElevenLabs timeout occurred",
                    service_name="ElevenLabs"
                )

            if error_type == "server":
                raise TransientServiceError(
                    "ElevenLabs 503 Service Unavailable",
                    service_name="ElevenLabs"
                )

            if error_type == "auth":
                raise PermanentServiceError(
                    "ElevenLabs authentication failed",
                    service_name="ElevenLabs"
                )

        print("🔊 ElevenLabs TTS generated successfully")
        return "audio-bytes"
