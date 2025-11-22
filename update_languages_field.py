#!/usr/bin/env python3
"""
Script to update all clinic documents in Firebase to ensure languages field is a JSON array.
Converts string values to arrays and defaults to ["English"] if missing/Unknown.
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

def update_languages_field():
    """Update all clinic documents to have languages as an array"""
    clinics_ref = db.collection('clinics')
    docs = clinics_ref.stream()
    
    updated_count = 0
    total_count = 0
    
    for doc in docs:
        total_count += 1
        data = doc.to_dict()
        languages = data.get('languages')
        
        # Determine if update is needed
        needs_update = False
        new_languages = None
        
        if not languages or languages == 'N/A' or languages == 'Unknown':
            # Missing or Unknown -> default to ["English"]
            new_languages = ["English"]
            needs_update = True
        elif isinstance(languages, str):
            # String -> convert to array
            new_languages = [lang.strip() for lang in languages.split(',')]
            needs_update = True
        elif isinstance(languages, list):
            # Already an array
            if len(languages) == 0:
                # Empty array -> default to ["English"]
                new_languages = ["English"]
                needs_update = True
            else:
                # Already correct format
                needs_update = False
        
        if needs_update:
            doc.reference.update({'languages': new_languages})
            print(f"✅ Updated {doc.id}: {languages} -> {new_languages}")
            updated_count += 1
        else:
            print(f"⏭️  Skipped {doc.id}: already correct ({languages})")
    
    print(f"\n{'='*60}")
    print(f"📊 MIGRATION COMPLETE")
    print(f"{'='*60}")
    print(f"Total clinics: {total_count}")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {total_count - updated_count}")

if __name__ == "__main__":
    print("🔄 Starting languages field migration...\n")
    update_languages_field()
