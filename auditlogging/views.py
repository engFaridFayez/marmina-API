from rest_framework import permissions, viewsets
from .models import ActivityLog
from .serializers import ActivityLogSerializer
from rest_framework.pagination import PageNumberPagination

class LogPagination(PageNumberPagination):
    page_size = 10

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    pagination_class = LogPagination