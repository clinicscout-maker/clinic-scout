#!/usr/bin/env python3
"""
Debug: Check if location matching logic works
"""

# Test the logic
user_areas = ['Toronto']
clinic_city = 'Ontario Wide'

print(f"User areas: {user_areas}")
print(f"Clinic city: {clinic_city}")
print()

location_match = False
for area in user_areas:
    print(f"Checking area: '{area}'")
    print(f"  area.lower() == clinic_city.lower(): {area.lower() == clinic_city.lower()}")
    print(f"  'ontario wide' in area.lower(): {'ontario wide' in area.lower()}")
    print(f"  'ontario wide' in clinic_city.lower(): {'ontario wide' in clinic_city.lower()}")
    print(f"  clinic_city.lower() in area.lower(): {clinic_city.lower() in area.lower()}")
    print(f"  area.lower() in clinic_city.lower(): {area.lower() in clinic_city.lower()}")
    
    if (area.lower() == clinic_city.lower() or 
        'ontario wide' in area.lower() or 
        'all locations' in area.lower() or
        'ontario wide' in clinic_city.lower() or
        clinic_city.lower() in area.lower() or
        area.lower() in clinic_city.lower()):
        location_match = True
        print(f"  ✅ MATCH!")
        break
    else:
        print(f"  ❌ No match")

print(f"\nFinal result: {location_match}")
