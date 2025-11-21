#!/usr/bin/env python3
"""
End-to-End Purchase Flow Test for Clinic Scout

This script tests the complete payment flow:
1. Creates a test user in Firestore
2. Simulates a Ko-fi webhook payment
3. Verifies user is upgraded to premium
4. Verifies welcome SMS notification is logged

Usage:
    python tests/test_purchase_flow.py
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("❌ FAIL: firebase-admin not installed. Run: pip install firebase-admin")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("❌ FAIL: requests not installed. Run: pip install requests")
    sys.exit(1)

# Test Configuration
TEST_USER_EMAIL = "test_user_123@clinicscout.ca"
TEST_USER_PHONE = "+15550001234"
TEST_USER_ID = "test_user_e2e_123"

def print_step(step_num, description):
    """Print a formatted test step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)

def print_success(message):
    """Print success message"""
    print(f"✅ PASS: {message}")

def print_fail(message):
    """Print failure message"""
    print(f"❌ FAIL: {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  INFO: {message}")

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    print_step(1, "Initialize Firebase Admin SDK")
    
    key_path = "serviceAccountKey.json"
    if not os.path.exists(key_path):
        key_path = "../serviceAccountKey.json"
    
    if not os.path.exists(key_path):
        print_fail(f"serviceAccountKey.json not found")
        return None
    
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print_success("Firebase initialized successfully")
        return db
    except Exception as e:
        print_fail(f"Failed to initialize Firebase: {e}")
        return None

def create_test_user(db):
    """Create/reset test user in Firestore"""
    print_step(2, "Create/Reset Test User")
    
    try:
        user_ref = db.collection('users').document(TEST_USER_ID)
        user_ref.set({
            'email': TEST_USER_EMAIL,
            'phoneNumber': TEST_USER_PHONE,
            'isPremium': False,
            'province': 'ON',
            'areas': ['Toronto'],
            'languages': ['English'],
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        print_success(f"Test user created: {TEST_USER_EMAIL}")
        print_info(f"User ID: {TEST_USER_ID}")
        print_info(f"Phone: {TEST_USER_PHONE}")
        print_info(f"isPremium: False")
        
        print_info("Waiting 5 seconds for Firestore indexing...")
        time.sleep(5)
        
        return True
    except Exception as e:
        print_fail(f"Failed to create test user: {e}")
        return False

def get_kofi_token():
    """Retrieve Ko-fi verification token from .kofi_token file"""
    print_step(3, "Retrieve Ko-fi Verification Token")
    
    token_file = ".kofi_token"
    if not os.path.exists(token_file):
        print_fail(f"{token_file} not found")
        return None
    
    try:
        with open(token_file, 'r') as f:
            token = f.read().strip()
        
        print_success(f"Token retrieved: {token[:20]}...")
        return token
    except Exception as e:
        print_fail(f"Failed to read token: {e}")
        return None

def get_cloud_function_url():
    """Retrieve Cloud Function URL using gcloud"""
    print_step(4, "Retrieve Cloud Function URL")
    
    # First, get the project ID
    try:
        project_result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if project_result.returncode != 0 or not project_result.stdout.strip():
            print_fail("No GCP project configured. Run: gcloud config set project PROJECT_ID")
            return None
        
        project_id = project_result.stdout.strip()
        print_info(f"Using GCP project: {project_id}")
    except Exception as e:
        print_fail(f"Failed to get project ID: {e}")
        return None
    
    try:
        result = subprocess.run(
            ['gcloud', 'functions', 'describe', 'kofi_handler', 
             '--gen2', '--region=us-central1', '--project', project_id,
             '--format=value(serviceConfig.uri)'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print_fail(f"gcloud command failed: {result.stderr}")
            print_info("Make sure the Cloud Function is deployed")
            return None
        
        url = result.stdout.strip()
        if not url:
            print_fail("Cloud Function URL not found")
            return None
        
        print_success(f"Function URL: {url}")
        return url
    except subprocess.TimeoutExpired:
        print_fail("gcloud command timed out")
        return None
    except FileNotFoundError:
        print_fail("gcloud CLI not found. Please install Google Cloud SDK")
        return None
    except Exception as e:
        print_fail(f"Failed to get function URL: {e}")
        return None

def send_webhook_request(url, token):
    """Send Ko-fi webhook POST request"""
    print_step(5, "Simulate Ko-fi Webhook Payment")
    
    # Ko-fi webhook payload format
    webhook_data = {
        "verification_token": token,
        "message_id": f"test_{int(time.time())}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": "Subscription",
        "is_subscription_payment": True,
        "is_first_subscription_payment": True,
        "email": TEST_USER_EMAIL,
        "amount": "5.00",
        "currency": "USD",
        "from_name": "Test User",
        "message": "Test subscription payment"
    }
    
    print_info(f"Sending webhook to: {url}")
    print_info(f"Payment email: {TEST_USER_EMAIL}")
    print_info(f"Amount: $5.00 (subscription)")
    
    try:
        # Ko-fi sends data as form-encoded with 'data' field containing JSON
        response = requests.post(
            url,
            data={'data': json.dumps(webhook_data)},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print_success("Webhook request successful")
            return True
        else:
            print_fail(f"Webhook returned status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_fail("Webhook request timed out")
        return False
    except Exception as e:
        print_fail(f"Webhook request failed: {e}")
        return False

def verify_user_upgrade(db):
    """Verify user was upgraded to premium"""
    print_step(6, "Verify User Upgrade")
    
    print_info("Waiting 5 seconds for webhook processing...")
    time.sleep(5)
    
    try:
        user_ref = db.collection('users').document(TEST_USER_ID)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print_fail("Test user not found in Firestore")
            return False
        
        user_data = user_doc.to_dict()
        is_premium = user_data.get('isPremium', False)
        
        print_info(f"isPremium: {is_premium}")
        print_info(f"lastPaymentAmount: {user_data.get('lastPaymentAmount', 'N/A')}")
        print_info(f"isSubscription: {user_data.get('isSubscription', 'N/A')}")
        
        if is_premium:
            print_success("User successfully upgraded to premium")
            return True
        else:
            print_fail("User is still not premium")
            return False
    except Exception as e:
        print_fail(f"Failed to verify user upgrade: {e}")
        return False

def verify_transaction_logged(db):
    """Verify transaction was logged"""
    print_step(7, "Verify Transaction Logged")
    
    try:
        # Query transactions for this user
        transactions_ref = db.collection('transactions')
        query = transactions_ref.where('email', '==', TEST_USER_EMAIL).order_by('processedAt', direction=firestore.Query.DESCENDING).limit(1)
        
        docs = list(query.stream())
        
        if not docs:
            print_fail("No transaction found for test user")
            return False
        
        transaction = docs[0].to_dict()
        print_info(f"Transaction ID: {docs[0].id}")
        print_info(f"Amount: {transaction.get('amount', 'N/A')}")
        print_info(f"Email: {transaction.get('email', 'N/A')}")
        print_info(f"Is Subscription: {transaction.get('isSubscription', 'N/A')}")
        
        print_success("Transaction logged successfully")
        return True
    except Exception as e:
        print_fail(f"Failed to verify transaction: {e}")
        return False

def verify_welcome_sms_logged(db):
    """Verify welcome SMS notification was logged"""
    print_step(8, "Verify Welcome SMS Logged")
    
    try:
        # Query notifications for WELCOME type
        notifications_ref = db.collection('notifications')
        query = notifications_ref.where('type', '==', 'WELCOME').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5)
        
        docs = list(query.stream())
        
        if not docs:
            print_fail("No WELCOME notifications found")
            return False
        
        # Find notification for our test user
        found = False
        for doc in docs:
            notification = doc.to_dict()
            if notification.get('userId') == TEST_USER_ID:
                found = True
                print_info(f"Notification ID: {doc.id}")
                print_info(f"User ID: {notification.get('userId', 'N/A')}")
                print_info(f"Phone: {notification.get('phone', 'N/A')}")
                print_info(f"Type: {notification.get('type', 'N/A')}")
                print_info(f"Twilio SID: {notification.get('sid', 'N/A')}")
                print_success("Welcome SMS notification logged successfully")
                break
        
        if not found:
            print_fail(f"No WELCOME notification found for user {TEST_USER_ID}")
            return False
        
        return True
    except Exception as e:
        print_fail(f"Failed to verify SMS notification: {e}")
        return False

def cleanup_test_data(db):
    """Optional: Clean up test data"""
    print_step(9, "Cleanup (Optional)")
    
    try:
        # Optionally delete test user
        # db.collection('users').document(TEST_USER_ID).delete()
        print_info("Test data preserved for manual inspection")
        print_info(f"To clean up manually, delete user: {TEST_USER_ID}")
        return True
    except Exception as e:
        print_info(f"Cleanup note: {e}")
        return True

def main():
    """Main test execution"""
    print("\n" + "="*60)
    print("CLINIC SCOUT - END-TO-END PURCHASE FLOW TEST")
    print("="*60)
    
    # Track test results
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Step 1: Initialize Firebase
    db = initialize_firebase()
    if not db:
        print("\n❌ TEST SUITE FAILED: Cannot initialize Firebase")
        return 1
    results['total'] += 1
    results['passed'] += 1
    
    # Step 2: Create test user
    if not create_test_user(db):
        print("\n❌ TEST SUITE FAILED: Cannot create test user")
        return 1
    results['total'] += 1
    results['passed'] += 1
    
    # Step 3: Get Ko-fi token
    token = get_kofi_token()
    if not token:
        print("\n❌ TEST SUITE FAILED: Cannot retrieve Ko-fi token")
        return 1
    results['total'] += 1
    results['passed'] += 1
    
    # Step 4: Get Cloud Function URL
    url = get_cloud_function_url()
    if not url:
        print("\n❌ TEST SUITE FAILED: Cannot retrieve Cloud Function URL")
        return 1
    results['total'] += 1
    results['passed'] += 1
    
    # Step 5: Send webhook
    results['total'] += 1
    if send_webhook_request(url, token):
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n❌ TEST SUITE FAILED: Webhook request failed")
        return 1
    
    # Step 6: Verify user upgrade
    results['total'] += 1
    if verify_user_upgrade(db):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Step 7: Verify transaction logged
    results['total'] += 1
    if verify_transaction_logged(db):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Step 8: Verify SMS logged
    results['total'] += 1
    if verify_welcome_sms_logged(db):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Step 9: Cleanup
    cleanup_test_data(db)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    
    if results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! Purchase flow is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {results['failed']} TEST(S) FAILED. Please review the output above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
