#!/usr/bin/env python3
"""
Check user phone number status
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

user_id = '9Kc4nEGcuQNcjC5fu8Z3'
user_ref = db.collection('users').document(user_id)
user_doc = user_ref.get()

if user_doc.exists:
    user_data = user_doc.to_dict()
    print(f"User: {user_id}")
    print(f"Phone: {user_data.get('phoneNumber')}")
    print(f"Email: {user_data.get('email')}")
    print(f"Premium: {user_data.get('isPremium')}")
    print(f"Areas: {user_data.get('areas')}")
    print(f"Languages: {user_data.get('languages')}")
else:
    print("User not found")
