#!/usr/bin/env python3
"""Check for premium users in Firestore"""
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Query for premium users
users_ref = db.collection('users')
query = users_ref.where('isPremium', '==', True).limit(10)

print("🔍 Searching for premium users...\n")
premium_users = query.get()

if not premium_users:
    print("❌ No premium users found")
else:
    print(f"✅ Found {len(premium_users)} premium user(s):\n")
    for user_doc in premium_users:
        user_data = user_doc.to_dict()
        print(f"📋 User ID: {user_doc.id}")
        print(f"   Email: {user_data.get('email', 'N/A')}")
        print(f"   Phone: {user_data.get('phoneNumber', 'N/A')}")
        print(f"   Areas: {user_data.get('areas', [])}")
        print(f"   Province: {user_data.get('province', 'N/A')}")
        print(f"   Premium: {user_data.get('isPremium', False)}")
        print()
