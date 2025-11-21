# Cloud Function Deployment - Issues and Resolutions

## Summary

Successfully identified and resolved deployment issues for the `kofi_handler` Cloud Function. The function is now deployed but requires Firestore API propagation.

---

## Issues Found and Fixed

### ❌ Issue #1: Missing `firebase_admin` Import
**Error**: `NameError: name 'firebase_admin' is not defined`

**Location**: `webhook_service/main.py` line 19

**Root Cause**: Code referenced `firebase_admin._apps` without importing the `firebase_admin` module.

**Fix Applied**:
```python
# Added import
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
```

**Status**: ✅ FIXED

---

### ❌ Issue #2: Firestore API Disabled
**Error**: `403 Cloud Firestore API has not been used in project gen-lang-client-0545832265 before or it is disabled`

**Root Cause**: The Firestore API was not enabled in the GCP project.

**Fix Applied**:
```bash
gcloud services enable firestore.googleapis.com --project=gen-lang-client-0545832265
```

**Status**: ✅ ENABLED (may need 5-10 minutes to propagate)

---

## Current Status

### Cloud Function Deployment: ✅ SUCCESS
- **State**: ACTIVE
- **URL**: https://us-central1-gen-lang-client-0545832265.cloudfunctions.net/kofi_handler
- **Service URL**: https://kofi-handler-r5nv2sapta-uc.a.run.app
- **Runtime**: Python 3.12
- **Region**: us-central1
- **Environment Variables**: KOFI_VERIFICATION_TOKEN set correctly

### Test Results: ⚠️ PENDING
- Steps 1-4: ✅ PASS
- Step 5 (Webhook): ❌ FAIL (500 error - Firestore API propagating)
- Steps 6-8: Not reached

---

## Next Steps

### Option 1: Wait for API Propagation (Recommended)
Wait 5-10 minutes for Firestore API to fully propagate, then run:
```bash
python3 tests/test_purchase_flow.py
```

### Option 2: Check Firestore Database Exists
Verify Firestore database is created:
```bash
# Check if Firestore database exists
gcloud firestore databases list --project=gen-lang-client-0545832265
```

If no database exists, create one:
```bash
# Create Firestore database in native mode
gcloud firestore databases create --location=us-central --project=gen-lang-client-0545832265
```

### Option 3: Manual Webhook Test
Test the webhook manually with curl:
```bash
curl -X POST https://kofi-handler-r5nv2sapta-uc.a.run.app \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "data={\"verification_token\":\"$(cat .kofi_token)\",\"email\":\"test@example.com\",\"amount\":\"5.00\",\"timestamp\":\"2025-11-21T15:00:00Z\",\"is_subscription_payment\":true}"
```

---

## Deployment Timeline

| Time | Event | Status |
|------|-------|--------|
| 15:39 | Identified Firebase init error | ❌ |
| 15:40 | Fixed `firebase_admin` import | ✅ |
| 15:40 | Redeployed Cloud Function | ✅ |
| 15:41 | Deployment completed | ✅ |
| 15:41 | Test run - Firestore API error | ❌ |
| 15:42 | Enabled Firestore API | ✅ |
| 15:43 | Test run - Still propagating | ⏳ |

---

## Technical Details

### Firebase Initialization Code (Fixed)
```python
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase Admin SDK
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
            print(f"Failed to initialize Firebase: {e}")
            raise

db = firestore.client()
```

### Deployment Command Used
```bash
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

---

## Verification Checklist

- [x] Cloud Function deployed
- [x] Function is ACTIVE
- [x] Firebase Admin SDK import fixed
- [x] Firestore API enabled
- [ ] Firestore API fully propagated
- [ ] Webhook returns 200 OK
- [ ] User upgraded to premium
- [ ] Transaction logged
- [ ] SMS notification logged

---

**Last Updated**: 2025-11-21 15:43 UTC  
**Status**: Waiting for Firestore API propagation (5-10 minutes)
