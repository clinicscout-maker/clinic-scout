import os
from twilio.rest import Client

class NotificationManager:
    def __init__(self, db=None):
        self.enabled = os.environ.get("SMS_ENABLED", "false").lower() == "true"
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.from_number = os.environ.get("TWILIO_FROM_NUMBER")
        self.to_number = os.environ.get("TWILIO_TO_NUMBER")
        self.db = db  # Firestore client
        
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

    def send_notification(self, message, clinic_id=None, user_id=None):
        """
        Send SMS notification and log to Firestore.
        
        Args:
            message: SMS body text
            clinic_id: ID of the clinic that triggered the alert
            user_id: ID of the user receiving the alert
        """
        if not self.enabled:
            print(f"[LOG ONLY] Notification: {message}")
            return

        try:
            sms_message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            print(f"SMS sent: {sms_message.sid}")
            
            # Log to Firestore if db is available
            if self.db and clinic_id and user_id:
                try:
                    from firebase_admin import firestore
                    self.db.collection('notifications').add({
                        'clinicId': clinic_id,
                        'userId': user_id,
                        'phone': self.to_number,
                        'type': 'CLINIC_ALERT',
                        'sid': sms_message.sid,
                        'timestamp': firestore.SERVER_TIMESTAMP
                    })
                    print(f"✅ Clinic alert logged: {sms_message.sid}")
                except Exception as e:
                    print(f"❌ Failed to log notification: {e}")
                    
        except Exception as e:
            print(f"Failed to send SMS: {e}")

notifier = NotificationManager()
