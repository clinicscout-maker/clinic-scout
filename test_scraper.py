#!/usr/bin/env python3
"""
Quick test script to scrape a few clinics and upload to Firebase.
This tests the full pipeline without processing all 255 clinics.
"""

import asyncio
import sys
import os

# Add scraper directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.main import scrape_clinic, analyze_clinic_status, upload_to_firestore

async def test_scraper():
    """Test the scraper on 3 sample clinics"""
    
    # Test with 3 diverse clinics (Ontario, BC, Alberta)
    test_clinics = [
        {
            "name": "Appletree Medical Group",
            "url": "https://appletreemedicalgroup.com/patients/register-new-patient/",
            "province": "ON"
        },
        {
            "name": "Coal Harbour Medical",
            "url": "https://www.coalharbourmedical.com/new-patients",
            "province": "BC"
        },
        {
            "name": "Pinnacle Medical - Crowfoot",
            "url": "https://www.pinnaclemedicalcentres.com/locations/crowfoot",
            "province": "AB"
        }
    ]
    
    results = {}
    
    print("=" * 60)
    print("CLINIC SCOUT - TEST RUN")
    print("=" * 60)
    print(f"Testing {len(test_clinics)} clinics...")
    print()
    
    for clinic in test_clinics:
        url = clinic['url']
        print(f"📍 Testing: {clinic['name']} ({clinic['province']})")
        print(f"   URL: {url}")
        
        # Scrape
        print(f"   ⏳ Scraping...")
        text_content = await scrape_clinic(url)
        
        if text_content:
            # Analyze
            print(f"   🤖 Analyzing with Gemini...")
            result = await analyze_clinic_status(text_content)
            results[url] = result
            
            status = result.get('status', 'UNKNOWN')
            print(f"   ✅ Status: {status}")
            print(f"   📋 Clinic: {result.get('clinic_name', 'N/A')}")
            print(f"   📍 District: {result.get('district', 'N/A')}")
            print()
        else:
            results[url] = {"status": "ERROR", "reason": "Failed to retrieve content"}
            print(f"   ❌ Failed to scrape")
            print()
    
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    for url, data in results.items():
        status = data.get('status', 'UNKNOWN')
        name = data.get('clinic_name', 'Unknown')
        print(f"{status:12} | {name}")
    
    print()
    print("=" * 60)
    print("UPLOADING TO FIREBASE")
    print("=" * 60)
    
    await upload_to_firestore(results)
    
    print()
    print("✅ Test complete!")
    print()
    print("To run the full scraper on all 255 clinics:")
    print("  cd scraper")
    print("  source ../.venv/bin/activate")
    print("  export GEMINI_API_KEY='your_key_here'")
    print("  python main.py")

if __name__ == "__main__":
    asyncio.run(test_scraper())
