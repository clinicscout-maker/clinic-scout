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
    received_token = data.get('verification_token')
    if received_token != KOFI_VERIFICATION_TOKEN:
        print(f"❌ Token mismatch: received={received_token}, expected={KOFI_VERIFICATION_TOKEN}")
        return jsonify({'error': 'Invalid verification token'}), 403
    
    print(f"✅ Token verified successfully")
    
    # Extract payment details
    email = data.get('email')
    amount = data.get('amount')
    timestamp = data.get('timestamp')
    payment_type = data.get('type')  # Donation, Subscription, Commission, or Shop Order
    is_subscription = data.get('is_subscription_payment', False)
    is_first_subscription = data.get('is_first_subscription_payment', False)
    tier_name = data.get('tier_name')
    message_id = data.get('message_id')
    
    print(f"📦 Payment Details:")
    print(f"   Type: {payment_type}")
    print(f"   Email: {email}")
    print(f"   Amount: ${amount}")
    print(f"   Subscription: {is_subscription}")
    print(f"   First Subscription: {is_first_subscription}")
    print(f"   Tier: {tier_name}")
    print(f"   Message ID: {message_id}")
    
    if not email:
        print(f"❌ Missing email in payment data")
        return jsonify({'error': 'Missing email'}), 400
        
    # Sanitize email
    email = email.lower().strip()
    
    # Find user by email in Firestore
    print(f"🔍 Searching for user with email: {email}")
    users_ref = db.collection('users')
    query = users_ref.where('email', '==', email).limit(1)
    
    # Debug: Try to get all results
    try:
        docs = list(query.stream())
        print(f"📊 Query returned {len(docs)} result(s)")
        
        if not docs:
            # Debug: Try to list all users to see if collection is accessible
            all_users = list(users_ref.limit(5).stream())
            print(f"📊 Total users in collection (sample): {len(all_users)}")
            if all_users:
                sample_emails = [u.to_dict().get('email', 'NO_EMAIL') for u in all_users]
                print(f"📊 Sample emails: {sample_emails}")
            
            # No matching user – still return 200 so Ko-fi doesn't retry
            print(f"⚠️  User not found for email: {email}")
            return jsonify({'status': 'success', 'message': 'User not found'}), 200
    except Exception as e:
        print(f"❌ Query error: {e}")
        return jsonify({'error': 'Database query failed'}), 500
    
    user_doc = docs[0]
    user_id = user_doc.id
    user_ref = users_ref.document(user_id)
    
    print(f"✅ Found user: {user_id}")
    
    # Log transaction to Firestore BEFORE updating user
    try:
        transaction_data = {
            'userId': user_id,
            'email': email,
            'amount': amount,
            'timestamp': timestamp,
            'paymentType': payment_type,
            'isSubscription': is_subscription,
            'isFirstSubscription': is_first_subscription,
            'tierName': tier_name,
            'messageId': message_id,
            'rawPayload': data,
            'processedAt': firestore.SERVER_TIMESTAMP
        }
        db.collection('transactions').add(transaction_data)
        print(f'✅ Transaction logged for user {user_id}')
    except Exception as e:
        print(f'❌ Failed to log transaction: {e}')
    
    # Update user premium status
    try:
        update_data = {
            'isPremium': True,
            'premiumSince': firestore.SERVER_TIMESTAMP,
            'lastPaymentAmount': amount,
            'lastPaymentDate': timestamp,
            'isSubscription': is_subscription,
        }
        
        if tier_name:
            update_data['tierName'] = tier_name
        
        user_ref.update(update_data)
        print(f'✅ User {user_id} upgraded to premium')
    except Exception as e:
        print(f'❌ Failed to update user: {e}')
        return jsonify({'error': 'Failed to update user'}), 500
    
    # Send SMS if Twilio is configured and user has a phone number
    user_data = user_doc.to_dict()
    phone = user_data.get('phoneNumber')
    
    if phone and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            print(f'📱 Sending welcome SMS to {phone}')
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body='🎉 You are now a premium Clinic Scout user! You will receive instant SMS alerts.',
                from_=TWILIO_PHONE_NUMBER,
                to=phone,
            )
            
            print(f'✅ SMS sent: {message.sid}')
            
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
            print(f'❌ SMS send error: {e}')
    else:
        if not phone:
            print(f'ℹ️  No phone number for user {user_id}')
        else:
            print(f'ℹ️  Twilio not configured, skipping SMS')
    
    # Return 200 status code as required by Ko-fi API
    print(f'✅ Payment processed successfully for {email}')
    return jsonify({'status': 'success', 'message': 'Payment processed'}), 200
