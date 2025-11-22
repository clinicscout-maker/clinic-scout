#!/usr/bin/env python3
"""
Verify Firebase clinic data sync
Check that clinics have proper district and province fields
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict

# Initialize Firebase
key_path = "serviceAccountKey.json"
if not os.path.exists(key_path):
    key_path = "../serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("="*60)
print("FIREBASE CLINIC DATA VERIFICATION")
print("="*60)

# Fetch all clinics
clinics_ref = db.collection('clinics')
clinics = clinics_ref.stream()

# Statistics
total_clinics = 0
clinics_by_province = defaultdict(int)
districts_by_province = defaultdict(set)
clinics_with_missing_data = []

for clinic_doc in clinics:
    total_clinics += 1
    data = clinic_doc.to_dict()
    
    clinic_id = clinic_doc.id
    name = data.get('name', 'N/A')
    district = data.get('district')
    province = data.get('province')
    status = data.get('status', 'N/A')
    
    # Track by province
    if province:
        clinics_by_province[province] += 1
        if district:
            districts_by_province[province].add(district)
    
    # Check for missing critical fields
    if not district or not province:
        clinics_with_missing_data.append({
            'id': clinic_id,
            'name': name,
            'district': district,
            'province': province,
            'status': status
        })

print(f"\n📊 SUMMARY:")
print(f"   Total Clinics: {total_clinics}")
print(f"\n📍 By Province:")
for prov in sorted(clinics_by_province.keys()):
    print(f"   {prov}: {clinics_by_province[prov]} clinics")

print(f"\n🏙️  Unique Districts by Province:")
for prov in sorted(districts_by_province.keys()):
    districts = sorted(districts_by_province[prov])
    print(f"\n   {prov} ({len(districts)} districts):")
    for district in districts:
        print(f"      - {district}")

if clinics_with_missing_data:
    print(f"\n⚠️  CLINICS WITH MISSING DATA ({len(clinics_with_missing_data)}):")
    for clinic in clinics_with_missing_data[:10]:  # Show first 10
        print(f"\n   ID: {clinic['id']}")
        print(f"   Name: {clinic['name']}")
        print(f"   District: {clinic['district'] or 'MISSING'}")
        print(f"   Province: {clinic['province'] or 'MISSING'}")
        print(f"   Status: {clinic['status']}")
    
    if len(clinics_with_missing_data) > 10:
        print(f"\n   ... and {len(clinics_with_missing_data) - 10} more")
else:
    print(f"\n✅ All clinics have district and province data!")

print(f"\n{'='*60}")
print("✅ Verification Complete")
print(f"{'='*60}")
