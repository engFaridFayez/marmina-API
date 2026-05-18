from django.urls import path
from .views import alhan_by_family_term, audio_list, get_alhan, get_specific_folder,stream_audio

urlpatterns = [
    path('audio/', audio_list),
    path("stream/<str:file_id>/", stream_audio),
    path('alhan/', get_alhan),
    path('get_folder/', get_specific_folder),
]
