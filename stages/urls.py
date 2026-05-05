from django.urls import include, path
from rest_framework.routers import DefaultRouter

from stages import views


router = DefaultRouter()
router.register('families',views.FamilyViewSet,basename='families')
router.register('stages',views.StageViewSet,basename='stages')


urlpatterns = [
    path('',include(router.urls))
]
