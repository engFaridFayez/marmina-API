from rest_framework import serializers

from users.models import CustomUser
from .models import Stage, Family


class FamilySerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField(
        source='customuser_set.count',
        read_only=True
    )
    users = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            'id',
            'name',
            'year',
            'user_count',
            'users',
        ]

    def get_users(self, obj):
        from users.serializers import UserSerializer  # lazy import
        return UserSerializer(
            obj.customuser_set.all(),
            many=True,
            context={**self.context, 'exclude_family': True}  # ← tell UserSerializer to skip family
        ).data


class StageSerializer(serializers.ModelSerializer):
    families = FamilySerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = ['id', 'name', 'families']


# Check✅✅
class FamilyMiniSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Family
        fields = ["id", "name"]

class FamilyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "full_name", "role"]

class FamilyDetailSerializer(serializers.ModelSerializer):
    users = FamilyUserSerializer(
        source="customuser_set",
        many=True,
        read_only=True
    )
    class Meta:
        model = Family
        fields = [
            "id",
            "name",
            "year",
            "users"
        ]