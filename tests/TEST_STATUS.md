# End-to-End Purchase Flow Test - Status Report

## Test Script Created ✅
**Location**: `tests/test_purchase_flow.py`

The comprehensive test script has been created and is ready to validate the complete purchase flow including:
- User creation in Firestore
- Ko-fi webhook simulation
- User premium upgrade verification
- Transaction logging verification
- Welcome SMS notification logging verification

## Dependencies Installed ✅
- `requests` - HTTP library for webhook calls
- `firebase-admin` - Firestore database access

## Current Blocker ⚠️

### Cloud Function Deployment Status: FAILED

The test cannot run because the `kofi_handler` Cloud Function is in a **FAILED** state:

```bash
$ gcloud functions list --project=gen-lang-client-0545832265
NAME          STATE   TRIGGER       REGION       ENVIRONMENT
kofi_handler  FAILED  HTTP Trigger  us-central1  2nd gen
```

### Background Deployments Running

There are **3 deployment commands still running** in the background (for 10h54m - 10h56m):
```bash
gcloud functions deploy kofi_handler --gen2 --runtime python312 --trigger-htt...
```

These appear to be stuck or taking an unusually long time.

---

## Next Steps to Complete Testing

### Option 1: Check Current Deployment Status (Recommended)
Check the logs of the running deployment to see what's happening:

```bash
# Check the most recent deployment logs
gcloud functions logs read kofi_handler \
  --project=gen-lang-client-0545832265 \
  --region=us-central1 \
  --limit=50
```

### Option 2: Cancel and Redeploy
If the deployments are stuck, cancel them and redeploy:

```bash
# Kill the stuck deployment processes (in your terminal)
# Then redeploy:
cd webhook_service
gcloud functions deploy kofi_handler \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --source=. \
  --entry-point=kofi_handler \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars KOFI_VERIFICATION_TOKEN=$(cat ../.kofi_token) \
  --project=gen-lang-client-0545832265
```

### Option 3: Manual Test with Local Webhook
For immediate testing, you can run the webhook locally (already tested successfully earlier):

```bash
# Terminal 1: Start local webhook
cd webhook_service
GOOGLE_APPLICATION_CREDENTIALS=../serviceAccountKey.json \
KOFI_VERIFICATION_TOKEN=$(cat ../.kofi_token) \
functions-framework --target=kofi_handler --debug

# Terminal 2: Run modified test pointing to localhost:8080
```

---

## Test Script Usage (Once Function is Deployed)

### Prerequisites
1. ✅ Firebase Admin SDK initialized
2. ✅ `.kofi_token` file exists
3. ⚠️ Cloud Function deployed and accessible
4. ✅ GCP project configured: `gen-lang-client-0545832265`

### Run the Test
```bash
python3 tests/test_purchase_flow.py
```

### Expected Output
```
============================================================
CLINIC SCOUT - END-TO-END PURCHASE FLOW TEST
============================================================

STEP 1: Initialize Firebase Admin SDK
✅ PASS: Firebase initialized successfully

STEP 2: Create/Reset Test User
✅ PASS: Test user created: test_user_123@clinicscout.ca

STEP 3: Retrieve Ko-fi Verification Token
✅ PASS: Token retrieved

STEP 4: Retrieve Cloud Function URL
✅ PASS: Function URL: https://...

STEP 5: Simulate Ko-fi Webhook Payment
✅ PASS: Webhook request successful

STEP 6: Verify User Upgrade
✅ PASS: User successfully upgraded to premium

STEP 7: Verify Transaction Logged
✅ PASS: Transaction logged successfully

STEP 8: Verify Welcome SMS Logged
✅ PASS: Welcome SMS notification logged successfully

============================================================
TEST SUMMARY
============================================================
Total Tests: 8
Passed: 8 ✅
Failed: 0 ❌

🎉 ALL TESTS PASSED! Purchase flow is working correctly.
```

---

## What the Test Validates

### 1. User Upgrade Flow
- Creates test user with `isPremium: false`
- Sends webhook with $5.00 subscription payment
- Verifies user upgraded to `isPremium: true`
- Checks payment metadata saved correctly

### 2. Transaction Logging
- Verifies transaction saved to `transactions` collection
- Checks all payment details logged:
  - `userId`
  - `email`
  - `amount`
  - `isSubscription`
  - `rawPayload`
  - `processedAt` timestamp

### 3. SMS Notification Logging
- Verifies welcome SMS logged to `notifications` collection
- Checks notification details:
  - `userId`
  - `phone`
  - `type: "WELCOME"`
  - `sid` (Twilio message ID)
  - `timestamp`

---

## Troubleshooting

### If Test Fails at Step 4 (Cloud Function URL)
- Check function is deployed: `gcloud functions list --project=gen-lang-client-0545832265`
- Check function status: Should be `ACTIVE`, not `FAILED`
- Redeploy if necessary (see Option 2 above)

### If Test Fails at Step 5 (Webhook Request)
- Check Cloud Function logs: `gcloud functions logs read kofi_handler`
- Verify Ko-fi token matches: `cat .kofi_token`
- Check function permissions (should allow unauthenticated)

### If Test Fails at Step 6 (User Upgrade)
- Check webhook logs for errors
- Verify email matching logic in `webhook_service/main.py`
- Check Firestore rules allow webhook to write

### If Test Fails at Step 8 (SMS Logging)
- Verify Twilio credentials are set (optional for test)
- Check if SMS logging code is working in webhook
- Review `notifications` collection in Firestore

---

## Test Data Cleanup

The test creates a user with ID: `test_user_e2e_123`

To clean up after testing:
```bash
# Delete test user from Firestore
# (Can be done via Firebase Console or script)
```

The test script preserves data for manual inspection by default.

---

**Status**: Test script ready, waiting for Cloud Function deployment to complete
**Next Action**: Resolve Cloud Function deployment issue, then run test
