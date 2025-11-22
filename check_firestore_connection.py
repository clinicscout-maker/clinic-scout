#!/usr/bin/env python3
"""
Check which Firestore database the local script connects to
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    app = firebase_admin.initialize_app(cred)

db = firestore.client()

print("="*60)
print("FIRESTORE CONNECTION INFO")
print("="*60)

# Get project ID
print(f"\nProject ID: {app.project_id}")

# Try to get database info
print(f"\nDatabase: {db._database}")

# Count users
users_ref = db.collection('users')
users = list(users_ref.limit(10).stream())
print(f"\nTotal users (sample): {len(users)}")

if users:
    print(f"\nSample user IDs:")
    for user in users[:5]:
        data = user.to_dict()
        print(f"  - {user.id}: {data.get('email', 'NO_EMAIL')}")

print(f"\n{'='*60}")
