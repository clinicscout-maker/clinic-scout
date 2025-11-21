#!/usr/bin/env python3
"""
Seed Firebase with clinic data from clinic_seed.csv
This populates the database with all clinics WITHOUT scraping them.
The scraper can then be run periodically to update statuses.
"""

import csv
import os
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

def seed_firebase():
    """Seed Firebase with clinic data from CSV"""
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        from firebase_admin import firestore
    except ImportError:
        print("❌ firebase-admin not installed. Run: pip install firebase-admin")
        return
    
    # Check for service account key
    key_path = "serviceAccountKey.json"
    if not os.path.exists(key_path):
        print("❌ serviceAccountKey.json not found")
        return
    
    # Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    collection_ref = db.collection('clinics')
    
    # Read clinic_seed.csv
    clinics = []
    with open('clinic_seed.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clinics.append(row)
    
    print("=" * 60)
    print("CLINIC SCOUT - FIREBASE SEEDER")
    print("=" * 60)
    print(f"Found {len(clinics)} clinics in clinic_seed.csv")
    print()
    
    # Get Toronto time
    toronto_time = datetime.now(ZoneInfo("America/Toronto"))
    
    # Upload in batches
    batch = db.batch()
    count = 0
    
    for clinic in clinics:
        # Create document ID from clinic ID
        doc_id = clinic['id'].strip()
        doc_ref = collection_ref.document(doc_id)
        
        # Prepare data
        doc_data = {
            "name": clinic.get('name', 'Unknown Clinic'),
            "url": clinic.get('url', ''),
            "city": clinic.get('city', 'Unknown'),
            "province": clinic.get('province', 'Unknown'),
            "district": clinic.get('city', 'Unknown'),  # Use city as district for now
            "address": "N/A",  # Will be filled by scraper
            "phone": "N/A",  # Will be filled by scraper
            "status": "UNCERTAIN",  # Default status, will be updated by scraper
            "updatedAt": toronto_time,
            "vacancy": "Unknown",
            "languages": "Unknown",
            "evidence": "Not yet scraped",
            "success_count": 0,
            "failure_count": 0
        }
        
        batch.set(doc_ref, doc_data, merge=True)
        count += 1
        
        # Commit batch every 400 operations
        if count % 400 == 0:
            batch.commit()
            batch = db.batch()
            print(f"✅ Committed {count} clinics...")
    
    # Commit remaining
    if count % 400 != 0:
        batch.commit()
    
    print(f"✅ Successfully seeded {count} clinics to Firebase!")
    print()
    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Check your web app - clinics should now appear")
    print("2. Run the scraper to update statuses:")
    print("   cd scraper")
    print("   source ../.venv/bin/activate")
    print("   python main.py")
    print()
    print("⚠️  Note: Scraping 255 clinics will take several hours")
    print("   and use many Gemini API calls. Consider running")
    print("   it overnight or in smaller batches.")

if __name__ == "__main__":
    seed_firebase()
