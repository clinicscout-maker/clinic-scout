#!/usr/bin/env python3
"""
Test SMS alert by simulating a status flip from CLOSED to OPEN
This will trigger the send_alert_batch function
"""

import os
import sys
import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# Add scraper directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper'))

# Initialize Firebase
key_path = "serviceAccountKey.json"
if not os.path.exists(key_path):
    key_path = "../serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Import notification manager
from notifications import NotificationManager
notifier = NotificationManager(db=db)

async def send_alert_batch(clinic_name, clinic_url, clinic_city, clinic_languages):
    """
    Send SMS alerts to all premium users who have selected this clinic's location.
    """
    if not db or not notifier:
        print(f"  📧 Alert batch skipped (DB or notifier not available)")
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
            
            print(f"\n  👤 Checking user: {user_id}")
            print(f"     Phone: {user_phone}")
            print(f"     Areas: {user_areas}")
            print(f"     Languages: {user_languages}")
            
            # Skip if no phone number
            if not user_phone:
                print(f"     ❌ Skipped: No phone number")
                continue
            
            # Check if user has selected this location
            location_match = False
            if user_areas:
                for area in user_areas:
                    if (area.lower() == clinic_city.lower() or 
                        'ontario wide' in area.lower() or 
                        'all locations' in area.lower() or
                        clinic_city.lower() in area.lower()):
                        location_match = True
                        break
            
            if not location_match:
                print(f"     ❌ Skipped: Location mismatch")
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
                print(f"     ❌ Skipped: Language mismatch")
                continue
            
            # Send SMS to this user
            msg = f"🚨 CLINIC NOW OPEN! 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
            
            print(f"     ✅ MATCH! Sending SMS...")
            
            # Use Twilio to send to this specific user's phone
            try:
                if notifier.enabled and notifier.client:
                    sms_message = notifier.client.messages.create(
                        body=msg,
                        from_=notifier.from_number,
                        to=user_phone
                    )
                    print(f"     📱 SMS sent: {sms_message.sid}")
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
                else:
                    print(f"     [LOG ONLY] Would send to {user_phone}: {msg}")
                    alert_count += 1
                    
            except Exception as e:
                print(f"     ❌ Failed to send SMS: {e}")
        
        print(f"\n{'='*60}")
        if alert_count > 0:
            print(f"✅ Sent {alert_count} targeted alert(s)")
        else:
            print(f"ℹ️  No matching users for {clinic_city}")
        print(f"{'='*60}")
            
    except Exception as e:
        print(f"  ❌ Error in send_alert_batch: {e}")

async def test_alert():
    """Test the alert system"""
    
    print("="*60)
    print("TESTING SMS ALERT SYSTEM")
    print("="*60)
    
    # Test clinic data
    clinic_name = "TEST Toronto Medical Centre"
    clinic_url = "https://test-clinic.example.com"
    clinic_city = "Toronto"
    clinic_languages = ["English", "French"]
    
    print(f"\nTest Clinic:")
    print(f"  Name: {clinic_name}")
    print(f"  City: {clinic_city}")
    print(f"  Languages: {clinic_languages}")
    
    # Call the alert function
    await send_alert_batch(clinic_name, clinic_url, clinic_city, clinic_languages)

if __name__ == "__main__":
    asyncio.run(test_alert())
