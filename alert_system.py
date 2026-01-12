import time
import os
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
import playsound
import threading
import config

class AlertSystem:
    def __init__(self):
        self.last_sound_time = 0
        self.last_notification_time = 0

    def trigger_alert(self, detection_label):
        """
        Triggers the alert process: Sound + Notification (Email/SMS).
        """
        current_time = time.time()
        
        # 1. Play Sound (Non-blocking usually preferred, but playsound is simple)
        if current_time - self.last_sound_time > config.SOUND_COOLDOWN:
            print(f"[ALERT] Dangerous Animal Detected: {detection_label}! Playing Sound...")
            # We run sound in a thread to not block the video processing
            threading.Thread(target=self._play_sound, daemon=True).start()
            self.last_sound_time = current_time

        # 2. Send Notification
        if current_time - self.last_notification_time > config.NOTIFICATION_COOLDOWN:
            print(f"[ALERT] Sending Notification for: {detection_label}...")
            
            if config.NOTIFICATION_METHOD in ['EMAIL', 'BOTH']:
                self._send_email(detection_label)
            
            if config.NOTIFICATION_METHOD in ['SMS', 'BOTH']:
                self._send_sms(detection_label)
                
            self.last_notification_time = current_time

    def _play_sound(self):
        try:
            if os.path.exists(config.ALERT_SOUND_PATH):
                # playsound 1.2.2 is often more stable on Windows than 1.3.0
                playsound.playsound(config.ALERT_SOUND_PATH)
            else:
                print(f"[WARN] Sound file not found at {config.ALERT_SOUND_PATH}")
        except Exception as e:
            print(f"[ERROR] Failed to play sound: {e}")

    def _send_email(self, label):
        try:
            msg = EmailMessage()
            msg.set_content(f"WARNING: A dangerous animal ({label}) has been detected by the security system.")
            msg['Subject'] = f"Security Alert: {label} Detected!"
            msg['From'] = config.SENDER_EMAIL
            msg['To'] = config.RECIPIENT_EMAIL

            # Connect to Gmail SMTP (SSL)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
                smtp.send_message(msg)
            
            print("[SUCCESS] Email Alert sent.")
        except Exception as e:
            print(f"[ERROR] Failed to send Email: {e}")

    def _send_sms(self, label):
        try:
            client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"WARNING: Dangerous animal ({label}) detected!",
                from_=config.TWILIO_PHONE_NUMBER,
                to=config.RECIPIENT_PHONE_NUMBER
            )
            print(f"[SUCCESS] SMS Alert sent. SID: {message.sid}")
        except Exception as e:
            print(f"[ERROR] Failed to send SMS: {e}")

if __name__ == "__main__":
    # Test block
    alert = AlertSystem()
    alert.trigger_alert("Test Animal")
