import os
import sys

# Add current directory to path so we can import scraper modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scraper.notifications import notifier
except ImportError:
    print("Could not import notifier. Make sure you are running this from the project root.")
    sys.exit(1)

def test_send():
    print("Testing SMS notification...")
    print(f"Enabled: {notifier.enabled}")
    print(f"From: {notifier.from_number}")
    print(f"To: {notifier.to_number}")
    
    notifier.send_notification("Test message from Clinic Scout Debugger 🚀")

if __name__ == "__main__":
    # Load env vars if not already loaded (e.g. if running directly)
    # In a real scenario, source twilio_env.sh first
    if not os.environ.get("TWILIO_ACCOUNT_SID"):
        print("WARNING: Twilio environment variables not set.")
        print("Run: source twilio_env.sh")
    
    test_send()
