from rest_framework import viewsets

from stages.models import Child, Family, Servant, Stage
from stages.serializers import ChildSerialzer, FamilySerializer, ServantSerializer, StageSerializer

# Create your views here.

class ChildrenViewSet(viewsets.ModelViewSet):
    serializer_class= ChildSerialzer

    def get_queryset(self):
        return Child.objects.all().order_by('name')
    
class FamilyViewSet(viewsets.ModelViewSet):
    serializer_class = FamilySerializer

    def get_queryset(self):
        return Family.objects.all().order_by('year')
    
class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer

    def get_queryset(self):
        return Stage.objects.all().order_by('name')
    
class ServantViewSet(viewsets.ModelViewSet):
    serializer_class = ServantSerializer

    def get_queryset(self):
        return Servant.objects.all().order_by('name')