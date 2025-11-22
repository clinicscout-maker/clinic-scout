#!/usr/bin/env python3
"""
Check if premium users query works
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
key_path = "serviceAccountKey.json"
if not os.path.exists(key_path):
    key_path = "../serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Query premium users
users_ref = db.collection('users')
premium_users = users_ref.where('isPremium', '==', True).stream()

print("Premium Users:")
print("="*60)

count = 0
for user_doc in premium_users:
    count += 1
    user_data = user_doc.to_dict()
    print(f"\n{count}. User ID: {user_doc.id}")
    print(f"   Email: {user_data.get('email')}")
    print(f"   Phone: {user_data.get('phoneNumber')}")
    print(f"   Areas: {user_data.get('areas')}")
    print(f"   Languages: {user_data.get('languages')}")

print(f"\n{'='*60}")
print(f"Total premium users: {count}")
