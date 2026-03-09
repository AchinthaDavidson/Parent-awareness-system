"""
Firebase Connection Test Script
Verifies that the parentdashboard backend can connect to Firestore.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_service_account_exists():
    """Test if serviceAccountKey.json exists"""
    print("=" * 60)
    print("Testing Firebase Connection Setup")
    print("=" * 60)
    
    backend_root = Path(__file__).parent.parent
    service_account_path = backend_root / "serviceAccountKey.json"
    
    if not service_account_path.exists():
        print(f"✗ ERROR: serviceAccountKey.json not found at {service_account_path}")
        return False
    
    print(f"✓ Service account file found at: {service_account_path}")
    return True

def test_firebase_import():
    """Test if firebase_admin can be imported"""
    try:
        import firebase_admin
        print("✓ firebase_admin imported successfully")
        return True
    except ImportError as e:
        print(f"✗ ERROR: Could not import firebase_admin: {e}")
        print("  Run: pip install firebase-admin")
        return False

def test_firestore_client():
    """Test if we can get a Firestore client"""
    try:
        from parentdashboard.data.firebase_client import get_firestore_client
        db = get_firestore_client()
        print("✓ Firestore client initialized")
        return db
    except Exception as e:
        print(f"✗ ERROR: Could not initialize Firestore: {e}")
        return None

def test_firestore_connection(db):
    """Test actual Firestore connection"""
    if db is None:
        return False
    
    try:
        # Try to read from users collection
        users_ref = db.collection("users")
        docs = list(users_ref.limit(1).stream())
        
        if docs:
            print(f"✓ Firestore connection successful!")
            print(f"  Found {len(docs)} user(s) (sample query)")
            doc_data = docs[0].to_dict()
            print(f"  Sample user data: {list(doc_data.keys())[:3]}...")
        else:
            print("⚠ Firestore connected but no users found")
            print("  This is OK if your database is empty")
        
        return True
    except Exception as e:
        print(f"✗ ERROR: Firestore query failed: {e}")
        print("  Check:")
        print("  1. Firebase project has Firestore enabled")
        print("  2. Service account has proper permissions")
        print("  3. Network/firewall allows Google Cloud access")
        return False

def test_project_config():
    """Test project configuration"""
    try:
        import json
        backend_root = Path(__file__).parent.parent
        service_account_path = backend_root / "serviceAccountKey.json"
        
        with open(service_account_path, 'r') as f:
            config = json.load(f)
        
        project_id = config.get('project_id', 'unknown')
        client_email = config.get('client_email', 'unknown')
        
        print(f"✓ Project configuration loaded")
        print(f"  Project ID: {project_id}")
        print(f"  Service Account: {client_email}")
        return True
    except Exception as e:
        print(f"✗ ERROR: Could not load project config: {e}")
        return False

def main():
    print("\n")
    
    # Step 1: Check service account file
    if not test_service_account_exists():
        print("\n✗ Setup incomplete. Add serviceAccountKey.json to backend/ folder")
        return
    
    # Step 2: Check imports
    if not test_firebase_import():
        print("\n✗ Install dependencies: pip install firebase-admin")
        return
    
    # Step 3: Load config
    test_project_config()
    
    # Step 4: Initialize client
    db = test_firestore_client()
    
    # Step 5: Test connection
    print("\n")
    if test_firestore_connection(db):
        print("\n" + "=" * 60)
        print("✓ Firebase connection is working correctly!")
        print("=" * 60)
        print("\nYou can now run the server:")
        print("  python parentdashboard/main.py")
        print("\nOr test the full backend:")
        print("  python parentdashboard/test_backend.py")
    else:
        print("\n" + "=" * 60)
        print("⚠ Firebase connection test failed")
        print("=" * 60)
        print("\nTroubleshooting steps:")
        print("1. Check Firebase Console: https://console.firebase.google.com/project/huruwa-4b852")
        print("2. Verify Firestore is enabled for your project")
        print("3. Ensure service account has 'Cloud Datastore User' role")
        print("4. Check network connectivity to Google Cloud")
    
    print("\n")

if __name__ == "__main__":
    main()
