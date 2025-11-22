#!/usr/bin/env python3
"""
Quick Payment Flow Test using existing user
Tests webhook with real user in database
"""

import os
import json
import requests
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Use existing user
USER_EMAIL = "tinschan4ca@gmail.com"
USER_ID = "626IFlTYzrUBi8sdeYyNE1jbLyx2"
WEBHOOK_URL = "https://kofi-handler-n6gaqa3rpa-uc.a.run.app"  # Updated to clinicscout-9fcc5 project

# Read token
with open('.kofi_token', 'r') as f:
    TOKEN = f.read().strip()

print("="*60)
print("QUICK PAYMENT FLOW TEST")
print("="*60)

# Step 1: Check user before
print(f"\n1️⃣ Checking user before payment...")
user_ref = db.collection('users').document(USER_ID)
user_doc = user_ref.get()
if user_doc.exists:
    data = user_doc.to_dict()
    print(f"✅ User found: {USER_EMAIL}")
    print(f"   isPremium BEFORE: {data.get('isPremium', False)}")
    original_premium = data.get('isPremium', False)
else:
    print(f"❌ User not found")
    exit(1)

# Step 2: Send webhook
print(f"\n2️⃣ Sending Ko-fi webhook...")
payload = {
    "verification_token": TOKEN,
    "message_id": f"test-{int(time.time())}",
    "timestamp": "2025-11-22T17:00:00Z",
    "type": "Subscription",
    "is_public": True,
    "from_name": "Test User",
    "message": None,
    "amount": "5.00",
    "url": "https://ko-fi.com/test",
    "email": USER_EMAIL,
    "currency": "USD",
    "is_subscription_payment": True,
    "is_first_subscription_payment": True,
    "kofi_transaction_id": f"test-txn-{int(time.time())}",
    "shop_items": None,
    "tier_name": "Premium Member",
    "shipping": None
}

response = requests.post(
    WEBHOOK_URL,
    data={'data': json.dumps(payload)},
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    timeout=10
)

print(f"   Status: {response.status_code}")
print(f"   Response: {response.text}")

if response.status_code != 200:
    print(f"❌ Webhook failed")
    exit(1)

# Step 3: Wait and check user after
print(f"\n3️⃣ Waiting 3 seconds...")
time.sleep(3)

print(f"\n4️⃣ Checking user after payment...")
user_doc = user_ref.get()
if user_doc.exists:
    data = user_doc.to_dict()
    new_premium = data.get('isPremium', False)
    print(f"   isPremium AFTER: {new_premium}")
    print(f"   lastPaymentAmount: {data.get('lastPaymentAmount')}")
    print(f"   tierName: {data.get('tierName')}")
    
    if new_premium:
        print(f"\n✅ PAYMENT FLOW VERIFIED!")
        print(f"   User successfully upgraded to premium")
    else:
        print(f"\n⚠️  User not upgraded (may have already been premium)")
else:
    print(f"❌ User not found after payment")

print(f"\n{'='*60}")
