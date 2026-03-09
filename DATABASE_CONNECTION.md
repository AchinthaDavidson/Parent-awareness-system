# Database Connection Guide - Parent Dashboard

## ✅ Your Database is Already Connected!

Your `serviceAccountKey.json` file is in the correct location and the Firebase connection is pre-configured.

## Current Setup

### 1. Service Account Location
```
backend/
└── serviceAccountKey.json    ← Your Firebase credentials (already here!)
```

### 2. How It Works

The parentdashboard backend automatically connects to Firebase through:

**File**: `parentdashboard/data/firebase_client.py`

```python
# Automatically finds serviceAccountKey.json
backend_root = Path(__file__).resolve().parents[2]
service_account_path = backend_root / "serviceAccountKey.json"

# Initializes Firebase Admin SDK
cred = credentials.Certificate(str(service_account_path))
firebase_admin.initialize_app(cred)

# Returns Firestore client
firestore.client()
```

### 3. What Database It Connects To

Based on your `serviceAccountKey.json`:

- **Project ID**: `huruwa-4b852`
- **Database**: Firestore (default database)
- **Service Account**: `firebase-adminsdk-fbsvc@huruwa-4b852.iam.gserviceaccount.com`

## Firestore Database Structure

The app reads from this path:

```
users/{child_user_id}/sessions/{sessionId}/practice/{practiceId}/attempts
```

### Data Flow

1. **Users Collection**: Contains child profiles
   ```
   users/{child_user_id}
   ├── name: "Child Name"
   ├── age: 5
   └── ...
   ```

2. **Sessions Subcollection**: Practice sessions
   ```
   users/{child_user_id}/sessions/{sessionId}
   ├── created_at: timestamp
   ├── request: { letter: "ක", mode: "starts_with", ... }
   └── objects: [...] (legacy data)
   ```

3. **Practice Subcollection**: Individual practices within session
   ```
   users/{child_user_id}/sessions/{sessionId}/practice/{practiceId}
   ├── created_at: timestamp
   └── word_progress: [{ status: "success", word: "සපත්තුව" }, ...]
   ```

4. **Attempts Subcollection**: Word-level attempts
   ```
   users/{child_user_id}/sessions/{sessionId}/practice/{practiceId}/attempts/{attemptId}
   ├── status: "success" | "wrong" | "pending"
   ├── word: "සපත්තුව"
   └── ...
   ```

## Testing the Connection

### Option 1: Quick Test Script

Run the test script to verify connection:

```bash
cd parentdashboard
python test_backend.py
```

This will test:
- ✓ Server startup
- ✓ Health endpoint
- ✓ PDF listing
- ✓ AI question (tests Groq + RAG)
- ✓ Speech progress (tests Firebase connection)

### Option 2: Manual API Test

Start the server:
```bash
python main.py
```

Then test speech progress endpoint:
```bash
curl "http://localhost:8000/parentdashboard/speech-progress?child_id=child_001"
```

Expected response (if Firebase has data):
```json
{
  "overall_accuracy": 75.5,
  "total_words": 100,
  "total_correct": 75,
  "phoneme_breakdown": [],
  "weekly_progress": [...]
}
```

If no data exists yet:
```json
{
  "overall_accuracy": 0.0,
  "total_words": 0,
  "total_correct": 0,
  "phoneme_breakdown": [],
  "weekly_progress": []
}
```

## Verifying Firebase Connection

### Check 1: Service Account File Exists

Your file is at: `d:/KONOVA/backend divyani/backend/serviceAccountKey.json`

✅ **Confirmed**: File exists with project `huruwa-4b852`

### Check 2: Dependencies Installed

```bash
pip install firebase-admin==7.2.0
```

Already included in `requirements.txt`

### Check 3: Initialize Firebase

The code automatically initializes Firebase when you import `get_firestore_client()`

No manual initialization needed!

## Common Issues & Solutions

### Issue 1: "Default Firebase App not found"

**Cause**: Firebase already initialized elsewhere

**Solution**: The code handles this with:
```python
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
```

### Issue 2: Permission Denied

**Cause**: Service account lacks Firestore permissions

**Solution**:
1. Go to [Firebase Console](https://console.firebase.google.com/project/huruwa-4b852)
2. IAM & Admin → Service Accounts
3. Ensure `firebase-adminsdk-fbsvc@huruwa-4b852.iam.gserviceaccount.com` has:
   - **Cloud Datastore User** role
   - **Firestore User** role

### Issue 3: No Data Showing

**Cause**: Database is empty or using wrong child IDs

**Solution**:
1. Check Firestore in Firebase Console
2. Verify documents exist at: `users/{uid}/sessions/...`
3. Use correct `child_id` in API requests

Default test ID: `sUXK8GwJC6QNPQ7PCxSXEzT3TH63` (from config)

## Using the Database in Code

### Get Firestore Client

```python
from parentdashboard.data.firebase_client import get_firestore_client

# Get client (singleton)
db = get_firestore_client()

# Query data
users_ref = db.collection("users")
docs = users_ref.stream()

for doc in docs:
    print(f"{doc.id}: {doc.to_dict()}")
```

### Get Child Data

```python
from parentdashboard.services.service import (
    get_dashboard_stats,
    get_accuracy_from_latest_practice_per_session,
    get_monthly_practice_count,
    get_target_sounds_last_4_sessions
)

child_id = "your_child_uid"

# Get all dashboard stats
stats = get_dashboard_stats(child_id)

# Get specific metrics
accuracy = get_accuracy_from_latest_practice_per_session(child_id)
monthly_count = get_monthly_practice_count(child_id)
target_sounds = get_target_sounds_last_4_sessions(child_id)
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│   FastAPI Server (main.py)          │
│   Port: 8000                        │
└──────────────┬──────────────────────┘
               │
        ┌──────▼──────┐
        │  Routes     │
        │  (api/)     │
        └──────┬──────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────┐      ┌──────▼──────┐
│ Services │      │ QA Service  │
│ (stats)  │      │ (RAG+LLM)   │
└───┬──────┘      └──────┬──────┘
    │                     │
┌───▼──────────────────────▼──────┐
│   Firebase Client               │
│   (firebase_client.py)          │
└───────────────┬─────────────────┘
                │
        ┌───────▼────────┐
        │ serviceAccount │
        │ Key.json       │
        └───────┬────────┘
                │
        ┌───────▼──────────────┐
        │ Firebase Firestore   │
        │ (huruwa-4b852)       │
        └──────────────────────┘
```

## Environment Variables (Optional)

You can add these to `.env` for advanced configuration:

```env
# Firebase (optional - uses serviceAccountKey.json by default)
FIREBASE_PROJECT_ID=huruwa-4b852

# Optional: Custom service account path
# FIREBASE_CREDENTIALS_PATH=/custom/path/to/key.json
```

## Next Steps

1. ✅ **Database is connected** - No action needed!
2. Test with: `python test_backend.py`
3. View data in [Firebase Console](https://console.firebase.google.com/project/huruwa-4b852/firestore)
4. Start the server: `python main.py`
5. Make API requests to fetch child data

## Support

If you encounter issues:

1. Check Firebase Console for data existence
2. Verify service account permissions
3. Check server logs for detailed errors
4. Run `test_backend.py` for diagnostics
