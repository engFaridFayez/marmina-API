from rest_framework import viewsets

from stages.models import Family, Stage
from stages.serializers import  FamilySerializer, StageSerializer

# Create your views here.

class FamilyViewSet(viewsets.ModelViewSet):
    serializer_class = FamilySerializer

    def get_queryset(self):
        return Family.objects.all().order_by('year')
    
class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer

    def get_queryset(self):
        return Stage.objects.all().order_by('name')
    
