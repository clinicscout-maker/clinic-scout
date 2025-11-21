import os
from twilio.rest import Client

class NotificationManager:
    def __init__(self):
        self.enabled = os.environ.get("SMS_ENABLED", "false").lower() == "true"
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.from_number = os.environ.get("TWILIO_FROM_NUMBER")
        self.to_number = os.environ.get("TWILIO_TO_NUMBER")
        
        if self.enabled and self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                print("Twilio client initialized.")
            except Exception as e:
                print(f"Failed to initialize Twilio client: {e}")
                self.enabled = False
        else:
            if self.enabled:
                print("SMS enabled but credentials missing.")
            self.enabled = False

    def send_notification(self, message):
        if not self.enabled:
            print(f"[LOG ONLY] Notification: {message}")
            return

        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            print(f"SMS sent: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

notifier = NotificationManager()
