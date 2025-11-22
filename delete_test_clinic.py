#!/usr/bin/env python3
"""
Delete test clinic to ensure fresh status flip test
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

clinic_id = 'test_clinic_ontario'
clinic_ref = db.collection('clinics').document(clinic_id)

# Delete the clinic
clinic_ref.delete()

print(f"✅ Deleted clinic: {clinic_id}")
print("📝 Now run the scraper to test fresh status flip (None → OPEN)")
