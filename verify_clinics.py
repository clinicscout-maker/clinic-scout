import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def verify_clinics():
    clinics_ref = db.collection('clinics')
    docs = clinics_ref.stream()
    
    count = 0
    print("\n--- Verifying Clinics in Firestore ---")
    for doc in docs:
        count += 1
        data = doc.to_dict()
        print(f"✅ Found Clinic: {data.get('name', 'Unknown')} (ID: {doc.id})")
        print(f"   Status: {data.get('status')}")
        print(f"   Updated: {data.get('updatedAt')}")
        if count >= 5:
            print("... and more (showing first 5)")
            break
    
    print(f"\nTotal documents found (in this sample): {count}")
    if count == 0:
        print("❌ No clinics found in Firestore yet.")
    else:
        print("✅ Data is present in Firestore.")

if __name__ == "__main__":
    verify_clinics()
