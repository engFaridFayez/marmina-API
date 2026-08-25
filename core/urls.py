from django.urls import path
from .views import KatamerosTodayView

urlpatterns = [
    # باقي الـ URLs عندك...
    
    path("katameros/today/", KatamerosTodayView.as_view()),
]