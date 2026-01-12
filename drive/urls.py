from django.urls import path
from .views import alhan_by_family_term, audio_list,stream_audio

urlpatterns = [
    path('audio/', audio_list),
    path('stream/<str:file_id>/', stream_audio),
    path('alhan/', alhan_by_family_term),
]
