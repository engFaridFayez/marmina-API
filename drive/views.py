from django.http import JsonResponse
from .services.google_drive import get_audio_files
from django.http import StreamingHttpResponse
from googleapiclient.http import MediaIoBaseDownload
import io
from .services.google_drive import get_drive_service,get_folder_id_by_name


ALHAN_ROOT = "1dnRGsewCsJuavg2CowLoAL7r0BwsZnCE"

TERM_MAP = {
    "1": "ترم اول",
    "2": "ترم تاني",
    "3": "ترم تالت"
}


def audio_list(request):
    FOLDER_ID = "1s48yhCXiCs0dPilPFnBx8sK-wXAQbN8Z"
    files = get_audio_files(FOLDER_ID)
    return JsonResponse(files, safe=False)



def stream_audio(request, file_id):
    service = get_drive_service()

    request_drive = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_drive)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)

    response = StreamingHttpResponse(
        fh,
        content_type='audio/mpeg'
    )
    response['Content-Disposition'] = 'inline; filename="audio.mp3"'
    return response


def alhan_by_family_term(request):
    family = request.GET.get('family')
    term = request.GET.get('term')

    if not family or term not in TERM_MAP:
        return JsonResponse({"error": "Invalid params"}, status=400)

    family_folder = get_folder_id_by_name(ALHAN_ROOT, family)
    term_folder = get_folder_id_by_name(family_folder, TERM_MAP[term])

    files = get_audio_files(term_folder)
    return JsonResponse(files, safe=False)