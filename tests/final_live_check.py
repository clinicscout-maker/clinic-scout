import asyncio
import os
import sys

# Add root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scraper functions
# This will also initialize Firebase and Notifier
from scraper.main import update_clinic_in_firestore, send_alert_batch, db

async def run_test():
    print("🚀 Starting Final Live Fire Test...")
    
    if not db:
        print("❌ Database not initialized. Check serviceAccountKey.json")
        return

    # 1. Define Test Target
    test_url = "https://appletreemedicalgroup.com/"
    # Generate ID exactly as scraper does
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
        'updatedAt': '2024-01-01T00:00:00Z' # Old timestamp
    }, merge=True)
    
    # Verify it's set
    doc = doc_ref.get()
    print(f"   Current Status in DB: {doc.to_dict().get('status')}")
    
    # 3. Simulate Analysis finding it OPEN
    print("\n🧠 Simulating Analysis finding it OPEN...")
    
    # Mock result that would come from analyze_clinic_status
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
    # We call update_clinic_in_firestore directly, which returns the OLD status
    print("\n💾 Updating Firestore with OPEN status...")
    old_status = await update_clinic_in_firestore(test_url, mock_result)
    print(f"   Old Status returned: {old_status}")
    
    # Check if alert logic would trigger
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
