#!/usr/bin/env python3
"""
Payment Flow Integration Test
Tests the complete purchase-to-premium flow including webhook processing
"""

import os
import sys
import time
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin
key_path = "../serviceAccountKey.json"
if not os.path.exists(key_path):
    key_path = "serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Test configuration
TEST_USER_EMAIL = "tinschan4ca@gmail.com"
TEST_USER_PHONE = "+15550001234"
TEST_USER_ID = "test_payment_flow_user"

# Read environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
KOFI_TOKEN_FILE = "../.kofi_token"  # Token file is in parent directory

def read_kofi_token():
    """Read Ko-fi verification token from file"""
    try:
        with open(KOFI_TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ Error: {KOFI_TOKEN_FILE} not found")
        return None

def create_dummy_user():
    """Create a test user in Firestore"""
    print("\n📝 Creating dummy user...")
    user_ref = db.collection('users').document(TEST_USER_ID)
    user_ref.set({
        'email': TEST_USER_EMAIL,
        'phoneNumber': TEST_USER_PHONE,
        'isPremium': False,
        'province': 'ON',
        'areas': ['Toronto'],
        'languages': ['English'],
        'createdAt': firestore.SERVER_TIMESTAMP,
        'updatedAt': firestore.SERVER_TIMESTAMP,
        'testUser': True  # Flag for easy identification
    })
    print(f"✅ Created user: {TEST_USER_ID}")
    print(f"   Email: {TEST_USER_EMAIL}")
    print(f"   Phone: {TEST_USER_PHONE}")
    print(f"   Province: ON")
    print(f"   Areas: ['Toronto']")
    print(f"   Languages: ['English']")
    print(f"   isPremium: False")
    
    # Wait for Firestore to index the new user
    print(f"\n⏳ Waiting 3 seconds for Firestore indexing...")
    time.sleep(3)

def simulate_kofi_webhook(token):
    """Send HTTP POST to webhook endpoint simulating Ko-fi payment"""
    print(f"\n🌐 Simulating Ko-fi webhook...")
    print(f"   URL: {WEBHOOK_URL}")
    
    # Ko-fi webhook payload format (matching official API documentation)
    payload = {
        "verification_token": token,
        "message_id": f"test-{int(time.time())}",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "type": "Subscription",
        "is_public": True,
        "from_name": "Test User",
        "message": None,
        "amount": "5.00",
        "url": "https://ko-fi.com/test",
        "email": TEST_USER_EMAIL,
        "currency": "USD",
        "is_subscription_payment": True,
        "is_first_subscription_payment": True,
        "kofi_transaction_id": f"test-txn-{int(time.time())}",
        "shop_items": None,
        "tier_name": "Premium Member",
        "shipping": None
    }
    
    # Ko-fi sends data as form-encoded with 'data' field containing JSON
    form_data = {
        'data': json.dumps(payload)
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ Webhook request successful")
            return True
        else:
            print(f"❌ Webhook request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return False

def verify_premium_upgrade(max_wait=10):
    """Poll Firestore to verify user was upgraded to premium"""
    print(f"\n🔍 Verifying premium upgrade (max {max_wait}s)...")
    
    user_ref = db.collection('users').document(TEST_USER_ID)
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            is_premium = user_data.get('isPremium', False)
            
            if is_premium:
                print(f"✅ User upgraded to premium!")
                print(f"   isPremium: {is_premium}")
                return True
            else:
                print(f"   ⏳ Waiting... isPremium: {is_premium}")
        
        time.sleep(2)
    
    print(f"❌ Timeout: User not upgraded after {max_wait}s")
    return False

def verify_welcome_notification():
    """Check if a WELCOME notification was logged"""
    print(f"\n📬 Verifying welcome notification...")
    
    notifications_ref = db.collection('notifications')
    query = notifications_ref.where('userId', '==', TEST_USER_ID).where('type', '==', 'WELCOME')
    notifications = list(query.stream())
    
    if notifications:
        print(f"✅ Found {len(notifications)} WELCOME notification(s)")
        for notif in notifications:
            data = notif.to_dict()
            print(f"   ID: {notif.id}")
            print(f"   Phone: {data.get('phone')}")
            print(f"   Timestamp: {data.get('timestamp')}")
        return True
    else:
        print("❌ No WELCOME notification found")
        return False

def cleanup():
    """Delete test user and notification logs"""
    print(f"\n🧹 Cleaning up test data...")
    
    # Delete user
    try:
        db.collection('users').document(TEST_USER_ID).delete()
        print(f"✅ Deleted user: {TEST_USER_ID}")
    except Exception as e:
        print(f"⚠️  Error deleting user: {e}")
    
    # Delete notifications
    try:
        notifications_ref = db.collection('notifications')
        query = notifications_ref.where('userId', '==', TEST_USER_ID)
        notifications = query.stream()
        
        count = 0
        for notif in notifications:
            notif.reference.delete()
            count += 1
        
        if count > 0:
            print(f"✅ Deleted {count} notification(s)")
    except Exception as e:
        print(f"⚠️  Error deleting notifications: {e}")

def run_test():
    """Main test execution"""
    print("="*60)
    print("PAYMENT FLOW INTEGRATION TEST")
    print("="*60)
    
    # Pre-flight checks
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL environment variable not set")
        print("   Set it with: export WEBHOOK_URL=https://your-function-url")
        return False
    
    kofi_token = read_kofi_token()
    if not kofi_token:
        print("❌ Ko-fi token not found")
        return False
    
    print(f"\n✅ Configuration loaded:")
    print(f"   Webhook URL: {WEBHOOK_URL}")
    print(f"   Ko-fi Token: {kofi_token[:10]}...")
    
    try:
        # Step 1: Setup
        create_dummy_user()
        
        # Step 2: Simulate payment webhook
        webhook_success = simulate_kofi_webhook(kofi_token)
        if not webhook_success:
            print("\n❌ FAILED: Webhook request failed")
            return False
        
        # Step 3: Verify premium upgrade
        premium_verified = verify_premium_upgrade(max_wait=10)
        if not premium_verified:
            print("\n❌ FAILED: Premium upgrade not detected")
            return False
        
        # Step 4: Verify welcome notification
        notification_verified = verify_welcome_notification()
        if not notification_verified:
            print("\n⚠️  WARNING: Welcome notification not found (may not be implemented)")
        
        # Success!
        print("\n" + "="*60)
        print("✅ PAYMENT FLOW VERIFIED")
        print("="*60)
        print("\n✓ User created")
        print("✓ Webhook processed")
        print("✓ Premium status updated")
        if notification_verified:
            print("✓ Welcome notification sent")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Step 5: Cleanup
        cleanup()

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
