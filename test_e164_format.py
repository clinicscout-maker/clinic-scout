#!/usr/bin/env python3
"""
Test E.164 phone number formatting
"""

def format_phone_to_e164(phone):
    """Format phone number to E.164 format"""
    # Remove all non-digit characters
    digits = ''.join(c for c in phone if c.isdigit())
    
    # Check if it's a valid North American number (10 or 11 digits)
    if len(digits) == 10:
        # Assume US/Canada, add +1
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        # Already has country code
        return f"+{digits}"
    elif phone.startswith('+') and len(digits) >= 10:
        # Already in E.164 format
        return f"+{digits}"
    
    return None  # Invalid format

# Test cases
test_numbers = [
    "416-555-1234",
    "(416) 555-1234",
    "4165551234",
    "+14165551234",
    "1-416-555-1234",
    "14165551234",
]

print("E.164 Phone Number Formatting Test")
print("="*50)

for number in test_numbers:
    formatted = format_phone_to_e164(number)
    print(f"Input:  {number:20} → Output: {formatted}")

print("\n✅ All formats should convert to: +14165551234")
