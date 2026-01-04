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


class ChildSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = [
            'id',
            'name',
            'birth_date',
            'phone',
            'parent_phone',
            'address',
            'father',
            'year_of_entrance',
            'year_of_graduation',
            'family'
        ]

    def to_representation(self, instance):
        self.fields['family'] = FamilySerializer(read_only=True)
        return super(ChildSerialzer,self).to_representation(instance)


class ServantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servant
        fields = [
            'id',
            'name',
            'birth_date',
            'address',
            'role',
            'stage',
            'family',
        ]
    def to_representation(self, instance):
        self.fields['stage'] = StageSerializer(read_only=True)
        self.fields['family'] = FamilySerializer(read_only=True)
        return super(ServantSerializer,self).to_representation(instance)




