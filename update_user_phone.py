#!/usr/bin/env python3
"""
Update phone number for user 9Kc4nEGcuQNcjC5fu8Z3 to E.164 format
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

def update_phone_number():
    """Update phone number to E.164 format"""
    
    user_id = '9Kc4nEGcuQNcjC5fu8Z3'
    
    # Get phone number from user
    phone_input = input("Enter phone number (any format, e.g., 416-555-1234): ").strip()
    
    # Format to E.164
    digits = ''.join(c for c in phone_input if c.isdigit())
    
    if len(digits) == 10:
        e164_phone = f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        e164_phone = f"+{digits}"
    elif phone_input.startswith('+') and len(digits) >= 10:
        e164_phone = f"+{digits}"
    else:
        print("❌ Invalid phone number format")
        return
    
    # Update in Firestore
    user_ref = db.collection('users').document(user_id)
    user_ref.update({'phoneNumber': e164_phone})
    
    print(f"\n✅ Phone number updated successfully!")
    print(f"   User ID: {user_id}")
    print(f"   Phone (E.164): {e164_phone}")
    print("\n🔔 User will now receive SMS alerts for Toronto clinics")

if __name__ == "__main__":
    update_phone_number()
