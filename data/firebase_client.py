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

    Initialization uses the service account key located at
    ``backend/serviceAccountKey.json``.
    """
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    # backend/parentdashboard/data/firebase_client.py -> parentdashboard/
    backend_root = Path(__file__).resolve().parents[1]
    service_account_path = backend_root / "serviceAccountKey.json"

    if not firebase_admin._apps:
        cred = credentials.Certificate(str(service_account_path))
        firebase_admin.initialize_app(cred)

    _firestore_client = firestore.client()
    return _firestore_client

