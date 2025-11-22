#!/usr/bin/env python3
"""
Verify test user exists and has correct email field
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Check if test user exists
user_id = "test_payment_flow_user"
email = "tinschan4ca@gmail.com"

print("="*60)
print("VERIFYING TEST USER")
print("="*60)

# Check by ID
print(f"\n1. Checking user by ID: {user_id}")
user_ref = db.collection('users').document(user_id)
user_doc = user_ref.get()

if user_doc.exists:
    data = user_doc.to_dict()
    print(f"✅ User exists")
    print(f"   Email in document: {data.get('email')}")
    print(f"   Phone: {data.get('phoneNumber')}")
    print(f"   isPremium: {data.get('isPremium')}")
else:
    print(f"❌ User does not exist")

# Check by email query
print(f"\n2. Checking user by email query: {email}")
users_ref = db.collection('users')
query = users_ref.where('email', '==', email).limit(1)
docs = list(query.stream())

if docs:
    print(f"✅ Found {len(docs)} user(s) with email {email}")
    for doc in docs:
        print(f"   User ID: {doc.id}")
        data = doc.to_dict()
        print(f"   Email: {data.get('email')}")
        print(f"   isPremium: {data.get('isPremium')}")
else:
    print(f"❌ No users found with email {email}")

print(f"\n{'='*60}")
