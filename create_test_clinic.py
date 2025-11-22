#!/usr/bin/env python3
"""
Script to create a dummy OPEN clinic in Firebase for testing SMS alerts.
Location: Toronto, ON
Status: OPEN (to trigger alert)
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

def create_test_clinic():
    """Create a test clinic with OPEN status for alert testing"""
    
    toronto_time = datetime.now(ZoneInfo("America/Toronto"))
    
    test_clinic_data = {
        'name': 'TEST Toronto Medical Centre',
        'address': '123 Test Street, Toronto, ON M5H 2N2',
        'district': 'Toronto',
        'phone': '416-555-0123',
        'status': 'OPEN',  # This will trigger the alert
        'updatedAt': toronto_time,
        'url': 'https://test-clinic.example.com',
        'vacancy': '5 spots available',
        'languages': ['English', 'French'],
        'evidence': 'TEST: Accepting new patients now!',
        'province': 'ON'
    }
    
    # Create test clinic (will be treated as NEW clinic since it doesn't exist)
    clinic_ref = db.collection('clinics').document('test_clinic_toronto_open')
    clinic_ref.set(test_clinic_data)
    
    print("✅ Test clinic created successfully!")
    print(f"   Clinic ID: test_clinic_toronto_open")
    print(f"   Name: {test_clinic_data['name']}")
    print(f"   Location: {test_clinic_data['district']}, {test_clinic_data['province']}")
    print(f"   Status: {test_clinic_data['status']}")
    print(f"   Languages: {test_clinic_data['languages']}")
    print("\n🔔 This clinic will trigger alerts for users with:")
    print("   - Location preference: Toronto (or Ontario Wide)")
    print("   - Language preference: English or French")
    print("\n⚠️  To test status flip, first set status to CLOSED, then update to OPEN")

if __name__ == "__main__":
    create_test_clinic()
