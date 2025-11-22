import asyncio
import os
import sys
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client

# --- CONFIGURATION ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "AC_PLACEHOLDER")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "AUTH_TOKEN_PLACEHOLDER")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "+1234567890")

# Initialize Firebase
key_path = "serviceAccountKey.json"
if not os.path.exists(key_path):
    key_path = "../serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
print("✅ Firebase initialized")

# Initialize Twilio
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print("✅ Twilio initialized")
except Exception as e:
    print(f"❌ Twilio init failed: {e}")
    twilio_client = None

# --- HELPER FUNCTIONS (Copied & Adapted) ---

async def update_clinic_in_firestore(url, data):
    """Updates a single clinic in Firestore immediately and returns old status"""
    if not db:
        return None

    try:
        collection_ref = db.collection('clinics')
        
        # Use ID from seed data if available
        doc_id = data.get('id')
        if not doc_id:
            doc_id = url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")

        doc_ref = collection_ref.document(doc_id)
        
        # Get old status before updating
        old_doc = doc_ref.get()
        old_status = old_doc.to_dict().get('status') if old_doc.exists else None
        
        toronto_time = datetime.now(ZoneInfo("America/Toronto"))
        
        # Ensure languages is stored as an array in Firestore
        languages = data.get('languages', ['English'])
        if isinstance(languages, str):
            languages = [l.strip() for l in languages.split(',')]
        
        doc_data = {
            "name": data.get('clinic_name', 'Unknown Clinic'),
            "address": data.get('address', 'N/A'),
            "district": data.get('district', 'N/A'),
            "phone": data.get('phone_number', 'N/A'),
            "status": data.get('status', 'UNKNOWN'),
            "updatedAt": toronto_time,
            "url": url,
            "vacancy": data.get('remaining_vacancy', 'N/A'),
            "languages": languages,  # Store as array
            "evidence": data.get('evidence', 'N/A'),
            "reason": data.get('reason', 'N/A'),
            "province": data.get('province', 'N/A')
        }
        
        doc_ref.set(doc_data, merge=True)
        print(f"   🔥 Firestore Updated: {data.get('status')} | Languages: {', '.join(languages)}")
        
        return old_status
        
    except Exception as e:
        print(f"   ❌ Firestore error: {e}")
        return None

async def send_alert_batch(clinic_name, clinic_url, clinic_city, clinic_languages, old_status=None):
    """
    Send SMS alerts to all premium users who have selected this clinic's location.
    """
    if not db or not twilio_client:
        print(f"  📧 Alert batch skipped (DB or Twilio not available)")
        return
    
    try:
        # Query all premium users
        users_ref = db.collection('users')
        premium_users = users_ref.where('isPremium', '==', True).stream()
        
        alert_count = 0
        
        for user_doc in premium_users:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            user_areas = user_data.get('areas', [])
            user_languages = user_data.get('languages', [])
            user_phone = user_data.get('phoneNumber')
            
            # Skip if no phone number
            if not user_phone:
                continue
            
            # Check if user has selected this location
            location_match = False
            if user_areas:
                for area in user_areas:
                    if (area.lower() == clinic_city.lower() or 
                        'ontario wide' in area.lower() or 
                        'all locations' in area.lower() or
                        'ontario wide' in clinic_city.lower() or
                        clinic_city.lower() in area.lower() or
                        area.lower() in clinic_city.lower()):
                        location_match = True
                        break
            
            if not location_match:
                continue
            
            # Check language match
            language_match = True
            if user_languages and clinic_languages:
                language_match = any(
                    any(user_lang.lower() in clinic_lang.lower() 
                        for clinic_lang in clinic_languages)
                    for user_lang in user_languages
                )
            
            if not language_match:
                continue
            
            # Send SMS to this user
            status_info = ""
            if old_status:
                status_info = f" ({old_status} -> OPEN)"
            elif old_status is None:
                status_info = " (NEW -> OPEN)"
            
            msg = f"🚨 CLINIC NOW OPEN!{status_info} 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
            
            try:
                sms_message = twilio_client.messages.create(
                    body=msg,
                    from_=TWILIO_FROM_NUMBER,
                    to=user_phone
                )
                print(f"  📱 SMS sent to {user_phone}: {sms_message.sid}")
                alert_count += 1
                
                # Log to Firestore
                db.collection('notifications').add({
                    'clinicName': clinic_name,
                    'clinicUrl': clinic_url,
                    'userId': user_id,
                    'phone': user_phone,
                    'type': 'STATUS_FLIP_ALERT',
                    'sid': sms_message.sid,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(f"  ❌ Failed to send SMS to {user_phone}: {e}")
        
        if alert_count > 0:
            print(f"  ✅ Sent {alert_count} targeted alert(s)")
        else:
            print(f"  ℹ️  No matching users for {clinic_city}")
            
    except Exception as e:
        print(f"  ❌ Error in send_alert_batch: {e}")

# --- MAIN TEST LOGIC ---

async def run_test():
    print("🚀 Starting Final Live Fire Test (Standalone)...")
    
    # 1. Define Test Target
    test_url = "https://appletreemedicalgroup.com/"
    test_id = test_url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
    
    print(f"🎯 Target: {test_url}")
    print(f"🆔 ID: {test_id}")
    
    # 2. Force Flip: Set to WAITLIST
    print(f"\n📝 Setting {test_url} to WAITLIST in Firestore...")
    doc_ref = db.collection('clinics').document(test_id)
    doc_ref.set({
        'status': 'WAITLIST',
        'district': 'Toronto',
        'province': 'ON',
        'languages': ['English'],
        'url': test_url,
        'name': 'Appletree Medical Group',
        'updatedAt': '2024-01-01T00:00:00Z'
    }, merge=True)
    
    # Verify
    doc = doc_ref.get()
    print(f"   Current Status in DB: {doc.to_dict().get('status')}")
    
    # 3. Simulate Analysis finding it OPEN
    print("\n🧠 Simulating Analysis finding it OPEN...")
    
    mock_result = {
        "clinic_name": "Appletree Medical Group (LIVE TEST)",
        "address": "123 Test St",
        "district": "Toronto",
        "phone_number": "416-555-0199",
        "remaining_vacancy": "10",
        "languages": ["English"],
        "status": "OPEN",
        "reason": "Test simulation of opening for Live Fire Check",
        "evidence": "We are now accepting new patients.",
        "province": "ON",
        "id": test_id
    }
    
    # 4. Trigger Update & Alert
    print("\n💾 Updating Firestore with OPEN status...")
    old_status = await update_clinic_in_firestore(test_url, mock_result)
    print(f"   Old Status returned: {old_status}")
    
    if old_status != "OPEN" and mock_result['status'] == "OPEN":
        print("\n🚨 Status Flip Detected! Triggering Alert Batch...")
        await send_alert_batch(
            clinic_name=mock_result['clinic_name'],
            clinic_url=test_url,
            clinic_city=mock_result['district'],
            clinic_languages=mock_result['languages'],
            old_status=old_status
        )
        print("\n✅ Test Complete. Check your phone for SMS!")
    else:
        print(f"\n❌ Status flip logic failed. Old: {old_status}, New: {mock_result['status']}")

if __name__ == "__main__":
    asyncio.run(run_test())
