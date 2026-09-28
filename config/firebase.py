import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Attempt to get the key from Render's cloud environment
firebase_env = os.environ.get("FIREBASE_CREDENTIALS")

if firebase_env:
    # We are live on Render
    cert_dict = json.loads(firebase_env)
    cred = credentials.Certificate(cert_dict)
else:
    # We are running locally on your computer
    cred = credentials.Certificate("firebase-key.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()