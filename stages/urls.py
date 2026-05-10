from django.urls import path

from stages import views

urlpatterns = [
    path("families/<int:pk>/",views.FamilyDetailView.as_view()),
    path("familiesusers/",views.FamilyListView.as_view()),
    path("stagesusers/",views.StageListView.as_view()),
]
