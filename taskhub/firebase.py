import os
import json
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = Path(__file__).resolve().parent

def _load_service_account() -> dict:
    raw = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON debe contener JSON válido.")
    path = BASE_DIR.parent / "firebase_service_account.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    raise RuntimeError(
        "No se encontró la configuración de Firebase. Defina FIREBASE_SERVICE_ACCOUNT_JSON o firebase_service_account.json."
    )

try:
    _service_account = _load_service_account()
except RuntimeError:
    _service_account = None

if _service_account:
    cred = credentials.Certificate(_service_account)
    app = firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    app = None
    db = None

def get_collection(name: str):
    if db is None:
        raise RuntimeError(
            "Firebase no está configurado. Defina FIREBASE_SERVICE_ACCOUNT_JSON o firebase_service_account.json para usar Firestore."
        )
    return db.collection(name)

def get_document(collection_name: str, doc_id: str):
    return get_collection(collection_name).document(doc_id)
