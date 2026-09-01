from rest_framework.generics import RetrieveAPIView ,ListAPIView
from stages.models import Family, Stage
from stages.serializers import  FamilyDetailSerializer, FamilySerializer, StageSerializer

# Create your views here.

class FamilyDetailView(RetrieveAPIView):
    serializer_class = FamilyDetailSerializer

    def get_queryset(self):
        user = self.request.user

        # أمين الشمامسة / Admin
        if user.role == "امين الشمامسة" or user.is_staff:
            return Family.objects.prefetch_related(
                "customuser_set",
                "stage__leaders",
            )

        # أمين مرحلة
        if user.role == "امين مرحلة":
            return Family.objects.filter(
                stage__leaders=user
            ).prefetch_related(
                "customuser_set",
                "stage__leaders",
            )

        # المستخدم ليس له أسرة
        if not user.family:
            return Family.objects.none()

        # أي مستخدم عادي:
        # يشوف أسرته فقط
        return Family.objects.filter(
            id=user.family.id
        ).prefetch_related(
            "customuser_set",
            "stage__leaders",
        )
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

        # امين اسرة / خادم
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
    