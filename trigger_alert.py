#!/usr/bin/env python3
"""
Trigger SMS alert by flipping clinic status from CLOSED to OPEN
This simulates what the scraper does when it detects a status flip
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
try:
    from notifications import NotificationManager
    notifier = NotificationManager(db=db)
except ImportError:
    print("⚠️  Could not import NotificationManager")
    notifier = None

async def send_alert_batch(clinic_name, clinic_url, clinic_city, clinic_languages):
    """Send SMS alerts to matching premium users"""
    if not db or not notifier:
        print(f"  📧 Alert batch skipped (DB or notifier not available)")
        return
    
    try:
        users_ref = db.collection('users')
        premium_users = users_ref.where('isPremium', '==', True).stream()
        
        alert_count = 0
        
        for user_doc in premium_users:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            user_areas = user_data.get('areas', [])
            user_languages = user_data.get('languages', [])
            user_phone = user_data.get('phoneNumber')
            
            print(f"\n  👤 User: {user_id}")
            print(f"     Phone: {user_phone}")
            print(f"     Areas: {user_areas}")
            
            if not user_phone:
                print(f"     ❌ No phone number")
                continue
            
            # Check location match
            location_match = False
            if user_areas:
                for area in user_areas:
                    if (area.lower() == clinic_city.lower() or 
                        'ontario wide' in area.lower() or 
                        'all locations' in area.lower()):
                        location_match = True
                        break
            
            if not location_match:
                print(f"     ❌ Location mismatch")
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
                print(f"     ❌ Language mismatch")
                continue
            
            msg = f"🚨 CLINIC NOW OPEN! 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
            
            print(f"     ✅ MATCH! Sending SMS...")
            
            try:
                if notifier.enabled and notifier.client:
                    sms_message = notifier.client.messages.create(
                        body=msg,
                        from_=notifier.from_number,
                        to=user_phone
                    )
                    print(f"     📱 SMS sent: {sms_message.sid}")
                    alert_count += 1
                else:
                    print(f"     [LOG ONLY] Would send to {user_phone}")
                    print(f"     Message: {msg}")
                    alert_count += 1
                    
            except Exception as e:
                print(f"     ❌ SMS failed: {e}")
        
        print(f"\n{'='*60}")
        if alert_count > 0:
            print(f"✅ Sent {alert_count} alert(s)")
        else:
            print(f"ℹ️  No matching users for {clinic_city}")
        print(f"{'='*60}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

async def trigger_alert():
    """Flip clinic to OPEN and trigger alerts"""
    
    print("="*60)
    print("TRIGGERING STATUS FLIP: CLOSED → OPEN")
    print("="*60)
    
    clinic_id = 'test_clinic_toronto_open'
    clinic_ref = db.collection('clinics').document(clinic_id)
    
    # Get old status
    clinic_doc = clinic_ref.get()
    if not clinic_doc.exists:
        print("❌ Test clinic not found. Run set_clinic_closed.py first.")
        return
    
    old_data = clinic_doc.to_dict()
    old_status = old_data.get('status')
    
    print(f"\n📋 Current Status: {old_status}")
    
    # Update to OPEN
    toronto_time = datetime.now(ZoneInfo("America/Toronto"))
    clinic_ref.update({
        'status': 'OPEN',
        'updatedAt': toronto_time,
        'evidence': 'TEST: Now accepting new patients!',
        'vacancy': '5 spots available'
    })
    
    print(f"✅ Status flipped: {old_status} → OPEN")
    
    # Trigger alerts
    clinic_name = old_data.get('name', 'TEST Toronto Medical Centre')
    clinic_url = old_data.get('url', 'https://test-clinic.example.com')
    clinic_city = old_data.get('district', 'Toronto')
    clinic_languages = old_data.get('languages', ['English', 'French'])
    
    print(f"\n🔔 Sending alerts for:")
    print(f"   Name: {clinic_name}")
    print(f"   City: {clinic_city}")
    print(f"   Languages: {clinic_languages}")
    
    await send_alert_batch(clinic_name, clinic_url, clinic_city, clinic_languages)

if __name__ == "__main__":
    asyncio.run(trigger_alert())
