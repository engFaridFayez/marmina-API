from rest_framework import serializers

from stages.models import *

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = [
            'id',
            'name',
        ]

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = [
            'id',
            'name',
            'year',
            'stage',
        ]
    def to_representation(self, instance):
        self.fields['stage'] = StageSerializer(read_only=True)
        return super(FamilySerializer,self).to_representation(instance)
