from rest_framework.generics import RetrieveAPIView ,ListAPIView
from stages.models import Family, Stage
from stages.serializers import  FamilyDetailSerializer, FamilySerializer, StageSerializer

# Create your views here.

class FamilyDetailView(RetrieveAPIView):
    queryset = Family.objects.prefetch_related(
        "customuser_set",
        "stage__leaders",
    ).all()

    serializer_class = FamilyDetailSerializer

class FamilyListView(ListAPIView):
    serializer_class = FamilySerializer

    def get_queryset(self):
        user = self.request.user

        # امين الشمامسة
        if user.role == "امين الشمامسة" or user.is_staff==True:
            return Family.objects.select_related("stage")

        # لو مفيش اسرة
        if not user.family:
            return Family.objects.none()

        # امين مرحلة
        if user.role == "امين مرحلة" :
            return Family.objects.filter(
                stage=user.family.stage
            ).select_related("stage")

        # امين اسرة / خادم عادي
        return Family.objects.filter(
            id=user.family.id
        ).select_related("stage")
    
class StageListView(ListAPIView):
    serializer_class = StageSerializer

    def get_queryset(self):
        user = self.request.user

        # امين الشمامسة
        if user.role == "امين الشمامسة" or user.is_staff==True:
            return Stage.objects.all()

        # امين مرحلة
        if user.role == "امين مرحلة":
            return Stage.objects.filter(
                leaders=user.id
            )

        # أي حد تاني → ملوش stages
        return Stage.objects.none()
    























# class FamilyViewSet(viewsets.ModelViewSet):
#     serializer_class = FamilySerializer

#     def get_queryset(self):
#         return Family.objects.all().order_by('year')
    
# class StageViewSet(viewsets.ModelViewSet):
#     serializer_class = StageSerializer

#     def get_queryset(self):
#         return Stage.objects.all().order_by('name')
    