#!/usr/bin/env python3
"""
Simulate a status flip by setting test clinic to CLOSED first
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# Initialize Firebase
key_path = "serviceAccountKey.json"
if not os.path.exists(key_path):
    key_path = "../serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def set_clinic_closed():
    """Set test clinic to CLOSED status"""
    
    clinic_id = 'test_clinic_toronto_open'
    clinic_ref = db.collection('clinics').document(clinic_id)
    
    # Check if clinic exists
    clinic_doc = clinic_ref.get()
    if not clinic_doc.exists:
        print("❌ Test clinic not found. Creating it first...")
        
        toronto_time = datetime.now(ZoneInfo("America/Toronto"))
        
        test_clinic_data = {
            'name': 'TEST Toronto Medical Centre',
            'address': '123 Test Street, Toronto, ON M5H 2N2',
            'district': 'Toronto',
            'phone': '416-555-0123',
            'status': 'CLOSED',
            'updatedAt': toronto_time,
            'url': 'https://test-clinic.example.com',
            'vacancy': 'N/A',
            'languages': ['English', 'French'],
            'evidence': 'TEST: Not accepting new patients (for testing)',
            'province': 'ON'
        }
        
        clinic_ref.set(test_clinic_data)
        print("✅ Test clinic created with CLOSED status")
    else:
        # Update to CLOSED
        toronto_time = datetime.now(ZoneInfo("America/Toronto"))
        clinic_ref.update({
            'status': 'CLOSED',
            'updatedAt': toronto_time,
            'evidence': 'TEST: Not accepting new patients (for testing)'
        })
        
        current_data = clinic_doc.to_dict()
        print("📋 Clinic status updated:")
        print(f"   Name: {current_data.get('name')}")
        print(f"   Location: {current_data.get('district')}")
        print(f"   Status: CLOSED")
    
    print("\n✅ Clinic is now CLOSED")
    print("📝 Next: Run 'python3 trigger_alert.py' to flip to OPEN and trigger SMS alerts")

if __name__ == "__main__":
    set_clinic_closed()
