#!/usr/bin/env python3
"""
Script to create a dummy test user in Firebase for testing SMS alerts.
Location: Toronto, ON
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

def create_test_user():
    """Create a test user for SMS alert testing"""
    
    test_user_data = {
        'email': 'test@clinicscout.ca',
        'phone': '+1234567890',  # Replace with your test phone number
        'isPremium': True,
        'areas': ['Toronto'],  # Location preference
        'languages': ['English'],
        'province': 'ON',
        'createdAt': firestore.SERVER_TIMESTAMP,
        'testUser': True  # Flag to identify test users
    }
    
    # Create or update test user
    user_ref = db.collection('users').document('test_user_toronto')
    user_ref.set(test_user_data, merge=True)
    
    print("✅ Test user created successfully!")
    print(f"   User ID: test_user_toronto")
    print(f"   Location: Toronto, ON")
    print(f"   Phone: {test_user_data['phone']}")
    print(f"   Premium: {test_user_data['isPremium']}")
    print(f"   Languages: {test_user_data['languages']}")
    print("\n⚠️  IMPORTANT: Update the 'phone' field with your actual test phone number!")
    print("   Run: db.collection('users').document('test_user_toronto').update({'phone': '+1XXXXXXXXXX'})")

if __name__ == "__main__":
    create_test_user()
