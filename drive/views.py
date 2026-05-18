import re

from django.http import HttpResponse, JsonResponse

from stages.models import Family
from .services.google_drive import get_all_audio_files, get_audio_files
from django.http import StreamingHttpResponse
from googleapiclient.http import MediaIoBaseDownload
import io
from .services.google_drive import get_drive_service,get_folder_id_by_name


ALHAN_ROOT = "1dnRGsewCsJuavg2CowLoAL7r0BwsZnCE"

TERM_MAP = {
    "1": "1- ترم اول",
    "2": "2- ترم تاني",
    "3": "3- ترم تالت"
}

FAMILY_MAP = {
    "1": "1- القديس اسطفانوس",
    "2": "2- مارمينا",
    "3": "3- الأنبا بيشوي",
    "4": "4- الأنبا انطونيوس",
    "5": "5- البابا كيرلس عمود الدين",
    "6": "6- البابا اثانسيوس الرسولي",
    "7": "7- الملاك سوريال",
    "8": "8- العدرا",
    "9": "9- الملاك ميخائيل",
}

def alhan_by_family_term(request):
    family_id = request.GET.get('family')
    term = request.GET.get('term')

    if family_id not in FAMILY_MAP or term not in TERM_MAP:
        return JsonResponse({"error": "Invalid params"}, status=400)

    family_name = FAMILY_MAP[family_id]

    family_folder = get_folder_id_by_name(ALHAN_ROOT, family_name)
    if not family_folder:
        return JsonResponse({"error": "Family folder not found"}, status=404)

    term_folder = get_folder_id_by_name(family_folder, TERM_MAP[term])
    if not term_folder:
        return JsonResponse({"error": "Term folder not found"}, status=404)
    
    files = get_audio_files(term_folder)
    print("FAMILY:", family_id)
    print("TERM:", term)
    print("FAMILY MAP:", FAMILY_MAP)
    print("FAMILY FOLDER:", family_folder)
    return JsonResponse(files, safe=False)


def audio_list(request):
    FOLDER_ID = "1s48yhCXiCs0dPilPFnBx8sK-wXAQbN8Z"
    files = get_audio_files(FOLDER_ID)
    return JsonResponse(files, safe=False)

def get_specific_folder(request):
    folder_name = request.GET.get('folder')
    files = get_audio_files(folder_name)
    return JsonResponse(files, safe=False)




# def stream_audio(request, file_id):
#     service = get_drive_service()

#     request_drive = service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request_drive)

#     done = False
#     while not done:
#         status, done = downloader.next_chunk()

#     fh.seek(0)

#     response = StreamingHttpResponse(
#         fh,
#         content_type='audio/mpeg'
#     )
#     response['Content-Disposition'] = 'inline; filename="audio.mp3"'
#     return response


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



# NEW
def get_alhan(request):
    family_id = request.GET.get("family")

    family = Family.objects.get(id=family_id)
    folder_id = family.drive_folder_id

    service = get_drive_service()  # ✅ لازم الأقواس

    files = get_all_audio_files(service, folder_id)

    return JsonResponse(files, safe=False)


import io
import re
import requests
from google.auth.transport.requests import Request
from django.http import HttpResponse

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