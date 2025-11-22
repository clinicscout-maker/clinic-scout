#!/usr/bin/env python3
"""
Export clinic data from Firebase to CSV
"""

import csv
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("="*60)
print("EXPORTING CLINIC DATA FROM FIREBASE TO CSV")
print("="*60)

# Fetch all clinics
print("\n📥 Fetching clinics from Firebase...")
clinics_ref = db.collection('clinics')
clinics = list(clinics_ref.stream())

print(f"✅ Found {len(clinics)} clinics")

# Prepare CSV data
csv_data = []
for clinic_doc in clinics:
    data = clinic_doc.to_dict()
    
    # Handle languages array
    languages = data.get('languages', [])
    if isinstance(languages, list):
        languages_str = ', '.join(languages)
    else:
        languages_str = str(languages)
    
    # Handle updatedAt timestamp
    updated_at = data.get('updatedAt')
    if updated_at:
        if hasattr(updated_at, 'to_dict'):
            updated_at_str = updated_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            updated_at_str = str(updated_at)
    else:
        updated_at_str = ''
    
    csv_data.append({
        'url': data.get('url', ''),
        'clinic_name': data.get('clinic_name', ''),
        'address': data.get('address', ''),
        'district': data.get('district', ''),
        'province': data.get('province', ''),
        'phone_number': data.get('phone_number', ''),
        'status': data.get('status', ''),
        'languages': languages_str,
        'remaining_vacancy': data.get('remaining_vacancy', ''),
        'reason': data.get('reason', ''),
        'evidence': data.get('evidence', ''),
        'updatedAt': updated_at_str
    })

# Sort by province and district
csv_data.sort(key=lambda x: (x['province'] or '', x['district'] or '', x['clinic_name'] or ''))

# Write to CSV
output_file = f"clinic_data/clinic_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
print(f"\n💾 Writing to {output_file}...")

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['url', 'clinic_name', 'address', 'district', 'province', 
                  'phone_number', 'status', 'languages', 'remaining_vacancy', 
                  'reason', 'evidence', 'updatedAt']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(csv_data)

print(f"✅ Exported {len(csv_data)} clinics to {output_file}")

# Print summary statistics
print(f"\n📊 Summary:")
print(f"   Total clinics: {len(csv_data)}")

# Count by status
status_counts = {}
for row in csv_data:
    status = row['status']
    status_counts[status] = status_counts.get(status, 0) + 1

print(f"\n   By Status:")
for status, count in sorted(status_counts.items()):
    print(f"      {status}: {count}")

# Count by province
province_counts = {}
for row in csv_data:
    province = row['province'] or 'Unknown'
    province_counts[province] = province_counts.get(province, 0) + 1

print(f"\n   By Province:")
for province, count in sorted(province_counts.items()):
    print(f"      {province}: {count}")

print(f"\n{'='*60}")
print(f"✅ Export complete!")
print(f"{'='*60}")
