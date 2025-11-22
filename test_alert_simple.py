#!/usr/bin/env python3
"""
Simple test to verify SMS alert system works
Uses the actual scraper code
"""

import os
import sys

# Set environment variables for testing
os.environ['SEED_FILE'] = 'test_alert_seed.csv'

# Create test seed file
with open('test_alert_seed.csv', 'w') as f:
    f.write('id,name,url,city,province\n')
    f.write('test_clinic_toronto_open,TEST Toronto Medical Centre,https://test-clinic.example.com,Toronto,ON\n')

print("="*60)
print("TESTING SMS ALERT SYSTEM")
print("="*60)
print("\n📋 Test Setup:")
print("   - Created test_alert_seed.csv with Toronto clinic")
print("   - Clinic status in Firebase: CLOSED")
print("   - Will run scraper to detect status flip")
print("\n🔄 Running scraper...")
print("="*60)
print()

# Run the actual scraper
os.system('set -a; source .env.local; set +a; venv/bin/python scraper/main.py')
