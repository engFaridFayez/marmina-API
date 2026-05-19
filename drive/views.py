from django.http import HttpResponse, JsonResponse
from stages.models import Family
from .services.google_drive import get_all_audio_files, get_audio_files
from google.auth.transport.requests import Request
from .services.google_drive import get_drive_service
import requests

def get_alhan(request):
    family_id = request.GET.get("family")

    family = Family.objects.get(id=family_id)
    folder_id = family.drive_folder_id

    service = get_drive_service()

    files = get_all_audio_files(service, folder_id)

    return JsonResponse(files, safe=False)


def stream_audio(request, file_id):
    service = get_drive_service()

    file_meta = service.files().get(
        fileId=file_id,
        fields="mimeType, name, size"
    ).execute()

    print("=== FILE META ===", file_meta)

    mime_type = file_meta.get("mimeType", "audio/mpeg")
    file_size = int(file_meta.get("size", 0))

    creds = service._http.credentials
    creds.refresh(Request())

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {
        "Authorization": f"Bearer {creds.token}",
    }

    drive_response = requests.get(url, headers=headers, stream=True)

    print("=== DRIVE STATUS ===", drive_response.status_code)
    print("=== DRIVE HEADERS ===", dict(drive_response.headers))
    print("=== FIRST 100 BYTES ===", drive_response.content[:100])

    data = drive_response.content

    response = HttpResponse(data, content_type=mime_type)
    response["Accept-Ranges"] = "bytes"
    response["Content-Length"] = str(len(data))
    return response





def audio_list(request):
    FOLDER_ID = "1s48yhCXiCs0dPilPFnBx8sK-wXAQbN8Z"
    files = get_audio_files(FOLDER_ID)
    return JsonResponse(files, safe=False)

def get_specific_folder(request):
    folder_name = request.GET.get('folder')
    files = get_audio_files(folder_name)
    return JsonResponse(files, safe=False)