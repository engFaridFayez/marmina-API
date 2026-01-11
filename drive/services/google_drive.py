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

def get_folder_id_by_name(parent_id, folder_name):
    service = get_drive_service()

    result = service.files().list(
        q=(
          f"'{parent_id}' in parents "
          f"and name='{folder_name}' "
          f"and mimeType='application/vnd.google-apps.folder'"
        ),
        fields="files(id, name)"
    ).execute()

    folders = result.get('files', [])
    return folders[0]['id'] if folders else None
