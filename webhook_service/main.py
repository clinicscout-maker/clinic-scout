"""
Ko-fi Webhook Handler for Google Cloud Functions (2nd Gen)

This function receives Ko-fi payment notifications and:
1. Verifies the webhook token
2. Updates the user's premium status in Firestore
3. Sends a confirmation SMS via Twilio (if configured)
"""

import os
import json
from flask import Request, jsonify
import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from twilio.rest import Client

# Initialize Firebase Admin SDK
# In Cloud Functions, this uses Application Default Credentials automatically
if not firebase_admin._apps:
    try:
        # Try ADC first (works in Cloud Functions)
        initialize_app()
    except Exception as e:
        # Fallback for local testing with service account key
        try:
            cred = credentials.Certificate('serviceAccountKey.json')
            initialize_app(cred)
        except Exception:
            # If both fail, let it fail - we need Firebase
            print(f"Failed to initialize Firebase: {e}")
            raise

db = firestore.client()

# Twilio configuration (environment variables)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Ko‑fi verification token (set via env var during deployment)
KOFI_VERIFICATION_TOKEN = os.getenv('KOFI_VERIFICATION_TOKEN')

@functions_framework.http
def kofi_handler(request: Request):
    """Handle Ko‑fi webhook POST requests."""
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    # Ko‑fi sends a form‑encoded payload with a "data" field containing JSON
    payload = request.form.get('data')
    if not payload:
        return jsonify({'error': 'Missing data field'}), 400

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Verify token
    if data.get('verification_token') != KOFI_VERIFICATION_TOKEN:
        return jsonify({'error': 'Invalid verification token'}), 403

    email = data.get('email')
    if not email:
        return jsonify({'error': 'Missing email'}), 400
        
    # Sanitize email
    email = email.lower().strip()
    
    print(f"🔍 Searching for user with email: {email}")

    amount = data.get('amount')
    timestamp = data.get('timestamp')
    is_subscription = data.get('is_subscription_payment', False)

    # Find user by email in Firestore
    users_ref = db.collection('users')
    query = users_ref.where('email', '==', email).limit(1)
    docs = list(query.stream())
    if not docs:
        # No matching user – still return 200 so Ko‑fi sees success
        return jsonify({'status': 'success', 'message': 'User not found'}), 200

    user_doc = docs[0]
    user_id = user_doc.id
    user_ref = users_ref.document(user_id)
    
    # Log transaction to Firestore BEFORE updating user
    try:
        db.collection('transactions').add({
            'userId': user_id,
            'email': email,
            'amount': amount,
            'timestamp': timestamp,
            'isSubscription': is_subscription,
            'rawPayload': data,
            'processedAt': firestore.SERVER_TIMESTAMP
        })
        print(f'✅ Transaction logged for user {user_id}')
    except Exception as e:
        print(f'❌ Failed to log transaction: {e}')
    
    # Update user premium status
    user_ref.update({
        'isPremium': True,
        'premiumSince': firestore.SERVER_TIMESTAMP,
        'lastPaymentAmount': amount,
        'lastPaymentDate': timestamp,
        'isSubscription': is_subscription,
    })

    # Send SMS if Twilio is configured and user has a phone number
    user_data = user_doc.to_dict()
    phone = user_data.get('phoneNumber')
    if phone and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body='🎉 You are now a premium Clinic Scout user! You will receive instant SMS alerts.',
                from_=TWILIO_PHONE_NUMBER,
                to=phone,
            )
            
            # Log notification to Firestore
            try:
                db.collection('notifications').add({
                    'userId': user_id,
                    'phone': phone,
                    'type': 'WELCOME',
                    'sid': message.sid,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                print(f'✅ Welcome SMS logged: {message.sid}')
            except Exception as e:
                print(f'❌ Failed to log notification: {e}')
                
        except Exception as e:
            # Log but do not fail the webhook
            print(f'SMS send error: {e}')

    return jsonify({'status': 'success', 'message': 'Payment processed'}), 200
