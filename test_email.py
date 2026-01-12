import smtplib
from email.message import EmailMessage
import config
import sys

def test_email():
    print("--- Testing Email Configuration ---")
    print(f"Sender: {config.SENDER_EMAIL}")
    print(f"Recipient: {config.RECIPIENT_EMAIL}")
    # Don't print the full password, just 'Yes' or 'No'
    print(f"Password provided: {'Yes' if config.SENDER_PASSWORD else 'No'}")

    try:
        msg = EmailMessage()
        msg.set_content("This is a test email from your Wild Animal Alert Project.")
        msg['Subject'] = "Test Alert System"
        msg['From'] = config.SENDER_EMAIL
        msg['To'] = config.RECIPIENT_EMAIL

        print("\nAttempting to connect to smtp.gmail.com:465...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            print("Connected. Logging in...")
            smtp.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
            print("Logged in. Sending message...")
            smtp.send_message(msg)
        
        print("\n[SUCCESS] Test email sent successfully! Check your inbox.")

    except smtplib.SMTPAuthenticationError as e:
        print("\n[ERROR] Authentication Failed.")
        print("Detailed Error:", e)
        print("\nPOSSIBLE FIX:")
        print("1. If using Gmail, you CANNOT use your regular login password.")
        print("2. You must enable 2-Step Verification on your Google Account.")
        print("3. Then go to https://myaccount.google.com/apppasswords")
        print("4. Generate a new App Password (select 'Mail' and 'Other').")
        print("5. Use that 16-character code in your config.py instead of your normal password.")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    test_email()
