#!/usr/bin/env python3
"""
Test the refined SMS message format with status flip information
"""

# Test different status flip scenarios

print("SMS Message Format Examples:")
print("="*60)

# Scenario 1: CLOSED → OPEN
old_status = "CLOSED"
clinic_name = "Toronto Medical Centre"
clinic_city = "Toronto"
clinic_url = "https://example.com"

status_info = f" ({old_status} → OPEN)"
msg = f"🚨 CLINIC NOW OPEN!{status_info} 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
print(f"\n1. Status Flip: CLOSED → OPEN")
print("-" * 60)
print(msg)

# Scenario 2: WAITLIST → OPEN
old_status = "WAITLIST"
status_info = f" ({old_status} → OPEN)"
msg = f"🚨 CLINIC NOW OPEN!{status_info} 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
print(f"\n2. Status Flip: WAITLIST → OPEN")
print("-" * 60)
print(msg)

# Scenario 3: NEW → OPEN (new clinic)
old_status = None
status_info = " (NEW → OPEN)"
msg = f"🚨 CLINIC NOW OPEN!{status_info} 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
print(f"\n3. New Clinic: NEW → OPEN")
print("-" * 60)
print(msg)

# Scenario 4: UNCERTAIN → OPEN
old_status = "UNCERTAIN"
status_info = f" ({old_status} → OPEN)"
msg = f"🚨 CLINIC NOW OPEN!{status_info} 🚨\n{clinic_name}\n{clinic_city}\n{clinic_url}"
print(f"\n4. Status Flip: UNCERTAIN → OPEN")
print("-" * 60)
print(msg)

print("\n" + "="*60)
print("✅ Users now see exactly what changed!")
