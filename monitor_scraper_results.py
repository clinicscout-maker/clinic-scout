#!/usr/bin/env python3
"""Monitor scraper results and SMS alerts"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("📊 Scraper Results Monitoring\n")
print("=" * 60)

# Check recent clinic updates
print("\n🏥 Recent Clinic Updates (Last 10 minutes):")
print("-" * 60)
clinics_ref = db.collection('clinics')
recent_time = datetime.now() - timedelta(minutes=10)

recent_clinics = clinics_ref.where('updatedAt', '>=', recent_time).limit(20).get()

if not recent_clinics:
    print("❌ No recent clinic updates found")
else:
    print(f"✅ Found {len(recent_clinics)} recently updated clinics:\n")
    for clinic_doc in recent_clinics:
        clinic_data = clinic_doc.to_dict()
        print(f"📍 {clinic_data.get('clinicName', 'Unknown')}")
        print(f"   Status: {clinic_data.get('status', 'N/A')}")
        print(f"   District: {clinic_data.get('district', 'N/A')}")
        print(f"   Province: {clinic_data.get('province', 'N/A')}")
        print(f"   Updated: {clinic_data.get('updatedAt', 'N/A')}")
        print()

# Check for OPEN clinics in Toronto
print("\n🟢 OPEN Clinics in Toronto/Downtown Toronto:")
print("-" * 60)
toronto_open = clinics_ref.where('status', '==', 'OPEN').where('province', '==', 'ON').limit(10).get()

if not toronto_open:
    print("❌ No OPEN clinics found in Ontario")
else:
    toronto_count = 0
    for clinic_doc in toronto_open:
        clinic_data = clinic_doc.to_dict()
        district = clinic_data.get('district', '')
        if 'Toronto' in district or 'Downtown' in district:
            toronto_count += 1
            print(f"✅ {clinic_data.get('clinicName', 'Unknown')}")
            print(f"   District: {district}")
            print(f"   Status: {clinic_data.get('status')}")
            print()
    
    if toronto_count == 0:
        print("❌ No OPEN clinics specifically in Toronto/Downtown Toronto")

# Check premium user
print("\n👤 Premium User Status:")
print("-" * 60)
user_ref = db.collection('users').document('osdsiavSHxUUNZ0ii1SXlNtSu7v2')
user_doc = user_ref.get()

if user_doc.exists:
    user_data = user_doc.to_dict()
    print(f"✅ User: {user_data.get('email')}")
    print(f"   Phone: {user_data.get('phoneNumber')}")
    print(f"   Areas: {user_data.get('areas')}")
    print(f"   Premium: {user_data.get('isPremium')}")
else:
    print("❌ User not found")

print("\n" + "=" * 60)
print("\n💡 Note: SMS alerts are sent when a clinic status changes from")
print("   WAITLIST/CLOSED to OPEN. Check your phone for SMS messages!")
