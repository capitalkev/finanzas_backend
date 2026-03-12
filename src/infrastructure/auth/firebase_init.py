import os

import firebase_admin
from firebase_admin import credentials


def initialize_firebase() -> None:
    """Inicializa Firebase Admin SDK en el microservicio SUNAT"""
    if not firebase_admin._apps:  # type: ignore
        token_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
        cred = credentials.Certificate(token_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK inicializado correctamente en SUNAT")
