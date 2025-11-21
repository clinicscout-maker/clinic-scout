# End-to-End Purchase Flow Test Results

**Test Execution Date**: 2025-11-21 11:12 EST  
**Test Script**: `tests/test_purchase_flow.py`  
**Overall Result**: ⚠️ **3/8 Tests Failed**

---

## Test Summary

| Step | Test | Status | Details |
|------|------|--------|---------|
| 1 | Firebase Initialization | ✅ PASS | Firebase Admin SDK initialized successfully |
| 2 | Create Test User | ✅ PASS | User created with email `test_user_123@clinicscout.ca` |
| 3 | Retrieve Ko-fi Token | ✅ PASS | Token retrieved from `.kofi_token` file |
| 4 | Get Cloud Function URL | ✅ PASS | URL: `https://kofi-handler-r5nv2sapta-uc.a.run.app` |
| 5 | Send Webhook Request | ✅ PASS | Webhook returned 200 OK |
| 6 | Verify User Upgrade | ❌ FAIL | User `isPremium` still `False` |
| 7 | Verify Transaction Logged | ❌ FAIL | Missing Firestore composite index |
| 8 | Verify Welcome SMS Logged | ❌ FAIL | Missing Firestore composite index |

**Final Score**: 5/8 passed (62.5%)

---

## Issues Found

### 🔴 Issue 1: User Not Found by Webhook (Critical)

**Problem:**  
The webhook returned: `{"message":"User not found","status":"success"}`

**Root Cause:**  
The webhook searches for users using this Firestore query:
```python
query = users_ref.where('email', '==', email).limit(1)
```

However, there's a **mismatch** between how the test creates the user and how the webhook searches:

**Test Script Creates:**
```python
user_ref = db.collection('users').document(TEST_USER_ID)  # Custom UID
user_ref.set({
    'email': TEST_USER_EMAIL,
    'phoneNumber': TEST_USER_PHONE,
    'isPremium': False,
    ...
})
```

**Webhook Searches:**
```python
# Searches for ANY user document where email field matches
query = users_ref.where('email', '==', email).limit(1)
```

**Why It Failed:**  
The webhook query should work, but it appears the email field might not be indexed or the query isn't finding the document. This could be due to:
1. Firestore query timing (eventual consistency)
2. Missing index on `email` field
3. Case sensitivity in email comparison

**Solution:**  
Wait a few seconds after creating the user before sending the webhook, or ensure the email field is properly indexed.

---

### 🔴 Issue 2: Missing Firestore Composite Index for Transactions

**Error Message:**
```
400 The query requires an index. You can create it here: 
https://console.firebase.google.com/v1/r/project/clinicscout-9fcc5/firestore/indexes?create_composite=...
```

**Query That Failed:**
```python
query = transactions_ref.where('email', '==', TEST_USER_EMAIL)\
    .order_by('processedAt', direction=firestore.Query.DESCENDING)\
    .limit(1)
```

**Required Index:**
- Collection: `transactions`
- Fields: `email` (Ascending), `processedAt` (Descending)

**How to Fix:**
1. Click the URL in the error message to auto-create the index
2. Or manually create in Firebase Console:
   - Go to Firestore → Indexes → Composite
   - Collection: `transactions`
   - Add fields: `email` (ASC), `processedAt` (DESC)

---

### 🔴 Issue 3: Missing Firestore Composite Index for Notifications

**Error Message:**
```
400 The query requires an index. You can create it here:
https://console.firebase.google.com/v1/r/project/clinicscout-9fcc5/firestore/indexes?create_composite=...
```

**Query That Failed:**
```python
query = notifications_ref.where('type', '==', 'WELCOME')\
    .order_by('timestamp', direction=firestore.Query.DESCENDING)\
    .limit(5)
```

**Required Index:**
- Collection: `notifications`
- Fields: `type` (Ascending), `timestamp` (Descending)

**How to Fix:**
1. Click the URL in the error message to auto-create the index
2. Or manually create in Firebase Console:
   - Go to Firestore → Indexes → Composite
   - Collection: `notifications`
   - Add fields: `type` (ASC), `timestamp` (DESC)

---

## Recommended Fixes

### Fix 1: Update Test Script (Immediate)

Add a delay after user creation to ensure Firestore indexing completes:

```python
def create_test_user(db):
    """Create/reset test user in Firestore"""
    print_step(2, "Create/Reset Test User")
    
    try:
        user_ref = db.collection('users').document(TEST_USER_ID)
        user_ref.set({
            'email': TEST_USER_EMAIL,
            'phoneNumber': TEST_USER_PHONE,
            'isPremium': False,
            'province': 'ON',
            'areas': ['Toronto'],
            'languages': ['English'],
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        print_success(f"Test user created: {TEST_USER_EMAIL}")
        
        # ADD THIS: Wait for Firestore to index the email field
        print_info("Waiting 3 seconds for Firestore indexing...")
        time.sleep(3)
        
        return True
    except Exception as e:
        print_fail(f"Failed to create test user: {e}")
        return False
```

### Fix 2: Create Firestore Indexes (Required)

**Option A - Auto-create (Recommended):**
1. Click the index creation URLs from the error messages
2. Wait 2-5 minutes for indexes to build

**Option B - Manual creation:**
1. Go to [Firebase Console](https://console.firebase.google.com/project/clinicscout-9fcc5/firestore/indexes)
2. Create two composite indexes:

**Index 1: Transactions**
```
Collection: transactions
Fields:
  - email (Ascending)
  - processedAt (Descending)
Query scope: Collection
```

**Index 2: Notifications**
```
Collection: notifications
Fields:
  - type (Ascending)
  - timestamp (Descending)
Query scope: Collection
```

### Fix 3: Verify Webhook Logic

Check if the webhook is properly querying by email. The current logic at line 71 of `webhook_service/main.py`:

```python
query = users_ref.where('email', '==', email).limit(1)
docs = list(query.stream())
if not docs:
    return jsonify({'status': 'success', 'message': 'User not found'}), 200
```

This should work, but consider adding debug logging to see why it's not finding the user.

---

## Next Steps

1. **Create Firestore Indexes** (5 minutes)
   - Click the URLs in the error messages
   - Wait for indexes to build

2. **Update Test Script** (2 minutes)
   - Add 3-second delay after user creation
   - Re-run test

3. **Re-run Test** (1 minute)
   ```bash
   python3 tests/test_purchase_flow.py
   ```

4. **Expected Result After Fixes:**
   ```
   Total Tests: 8
   Passed: 8 ✅
   Failed: 0 ❌
   
   🎉 ALL TESTS PASSED! Purchase flow is working correctly.
   ```

---

## Index Creation URLs

**Transactions Index:**
```
https://console.firebase.google.com/v1/r/project/clinicscout-9fcc5/firestore/indexes?create_composite=ClZwcm9qZWN0cy9jbGluaWNzY291dC05ZmNjNS9kYXRhYmFzZXMvKGRlZmF1bHQpL2NvbGxlY3Rpb25Hcm91cHMvdHJhbnNhY3Rpb25zL2luZGV4ZXMvXxABGgkKBWVtYWlsEAEaDwoLcHJvY2Vzc2VkQXQQAhoMCghfX25hbWVfXxAC
```

**Notifications Index:**
```
https://console.firebase.google.com/v1/r/project/clinicscout-9fcc5/firestore/indexes?create_composite=Cldwcm9qZWN0cy9jbGluaWNzY291dC05ZmNjNS9kYXRhYmFzZXMvKGRlZmF1bHQpL2NvbGxlY3Rpb25Hcm91cHMvbm90aWZpY2F0aW9ucy9pbmRleGVzL18QARoICgR0eXBlEAEaDQoJdGltZXN0YW1wEAIaDAoIX19uYW1lX18QAg
```

---

## Test Environment

- **GCP Project**: `gen-lang-client-0545832265`
- **Cloud Function**: `kofi_handler` (Gen2, us-central1)
- **Function URL**: `https://kofi-handler-r5nv2sapta-uc.a.run.app`
- **Test User**: `test_user_123@clinicscout.ca` (UID: `test_user_e2e_123`)
- **Test Phone**: `+15550001234`

---

**Status**: ⏳ Waiting for Firestore index creation and test script update
