from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
import os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

SERVICE_ACCOUNT_FILE = os.path.join(
    settings.BASE_DIR,
    'config',
    'angle-484008-d7827093322e.json'
)

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=creds)
    return service


def get_audio_files(folder_id):
    service = get_drive_service()

    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)"
    ).execute()

    return results.get('files', [])

# NEW

def get_all_audio_files(service, folder_id):
    results = []

    query = f"'{folder_id}' in parents and trashed=false"

    response = service.files().list(
        q=query,
        fields="files(id, name, mimeType)"
    ).execute()

    items = response.get("files", [])

    for item in items:

        if item["mimeType"] == "application/vnd.google-apps.folder":
            results.append({
                "type": "folder",
                "id": item["id"],
                "name": item["name"],
                "alhan": get_all_audio_files(service, item["id"])  # recursion
            })

        elif "audio" in item["mimeType"]:
            results.append({
                "type": "audio",
                "id": item["id"],
                "name": item["name"]
            })

    return results