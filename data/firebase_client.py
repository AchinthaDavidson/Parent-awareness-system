"""Firebase Admin / Firestore client for Parent Dashboard.

This module centralizes initialization of the firebase_admin SDK so that
other modules can safely import a Firestore client without duplicating
initialization logic.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore


_firestore_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Return a singleton Firestore client.

    On GCP (Cloud Run), uses Application Default Credentials automatically.
    Locally, falls back to serviceAccountKey.json.
    """
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    if not firebase_admin._apps:
        # Try local service account key first (for local dev)
        backend_root = Path(__file__).resolve().parents[1]
        service_account_path = backend_root / "serviceAccountKey.json"

        if service_account_path.exists():
            cred = credentials.Certificate(str(service_account_path))
            firebase_admin.initialize_app(cred)
        else:
            # On Cloud Run: use Application Default Credentials
            firebase_admin.initialize_app()

    _firestore_client = firestore.client()
    return _firestore_client

