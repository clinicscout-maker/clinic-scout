import argparse
import os
import time
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# Setup Firestore
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    except Exception:
        firebase_admin.initialize_app()

db = firestore.client()

def verify_handshake(webhook_url):
    email = "test_handshake@clinicscout.ca"
    user_id = "test_handshake_user"
    
    print(f"🚀 Starting verification for {email}...")

    # 1. Create temporary test user
    print("1️⃣ Creating test user...")
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'email': email,
        'isPremium': False,
        'createdAt': firestore.SERVER_TIMESTAMP
    })
    
    try:
        # 2. Send POST request to Webhook
        print(f"2️⃣ Sending webhook to {webhook_url}...")
        payload = {
            'verification_token': os.getenv('KOFI_VERIFICATION_TOKEN', 'test_token'), # Ensure this matches your deployed env or local test
            'email': "Test_Handshake@ClinicScout.ca ", # Mixed case and whitespace to test sanitization
            'amount': '5.00',
            'timestamp': '2023-10-27T10:00:00Z',
            'is_subscription_payment': True
        }
        
        # Ko-fi sends data as form-encoded 'data' field containing JSON
        response = requests.post(webhook_url, data={'data': json.dumps(payload)})
        
        print(f"   Response: {response.status_code} - {response.text}")
        
        if response.status_code != 200:
            print("❌ Webhook failed!")
            return

        # 3. Wait
        print("3️⃣ Waiting 5 seconds for processing...")
        time.sleep(5)

        # 4. Verify Firestore
        print("4️⃣ Verifying Firestore update...")
        user_doc = user_ref.get()
        if not user_doc.exists:
            print("❌ User document missing!")
            return

        data = user_doc.to_dict()
        is_premium = data.get('isPremium')
        
        if is_premium:
            print("✅ SUCCESS: User is now Premium!")
        else:
            print(f"❌ FAILURE: User isPremium is {is_premium}")

    finally:
        # 5. Cleanup
        print("5️⃣ Cleaning up...")
        user_ref.delete()
        print("✨ Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verify Ko-fi Webhook Handshake')
    parser.add_argument('--url', help='Webhook URL', required=True)
    args = parser.parse_args()
    
    verify_handshake(args.url)
