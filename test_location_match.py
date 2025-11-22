#!/usr/bin/env python3
"""
Test SMS alert with updated location matching logic
Uses actual scraper code with proper imports
"""

import os
import sys
import asyncio

# Set up environment
sys.path.insert(0, 'scraper')
os.chdir('/Users/tinshuichan/Library/Mobile Documents/com~apple~CloudDocs/Antigravity')

# Import from scraper
from scraper.main import send_alert_batch

async def test():
    print("="*60)
    print("TESTING SMS ALERT WITH UPDATED LOCATION LOGIC")
    print("="*60)
    
    # Test with Ontario Wide clinic
    clinic_name = "TEST Toronto Medical Centre"
    clinic_url = "https://test-clinic.example.com"
    clinic_city = "Ontario Wide"  # This should now match Toronto users
    clinic_languages = ["English", "French"]
    
    print(f"\nClinic Details:")
    print(f"  Name: {clinic_name}")
    print(f"  City: {clinic_city}")
    print(f"  Languages: {clinic_languages}")
    print(f"\nExpected: Should match user with areas=['Toronto']")
    print("="*60)
    
    await send_alert_batch(clinic_name, clinic_url, clinic_city, clinic_languages)

if __name__ == "__main__":
    asyncio.run(test())
