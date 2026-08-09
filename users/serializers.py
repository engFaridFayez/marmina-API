from rest_framework import serializers
from stages.models import Family
from stages.serializers import FamilyMiniSerializer, StageMiniSerializer
from users.models import CustomUser
from axes.handlers.proxy import AxesProxyHandler


class ProfileSerializer(serializers.ModelSerializer):
    family = FamilyMiniSerializer()
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'full_name',
            'first_name',
            'last_name',
            'birth_date',
            'joined_date',
            'email',
            'image',
            'address',
            'phone',
            'father',
            'role',
            'family',
            'slogan',
            'parent_phone',
            'whatsapp',
            'is_staff',

        ]

class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'password',
            'confirm_password',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

        def validate(self,attrs):
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError(
                "Password and Confirm Password do not match."
            )
            return attrs
        
        def create(self,validated_data):
            validated_data.pop('confirm_password')

            user = CustomUser.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password']
            )

            return user


class UserSerializer(serializers.ModelSerializer):
    family = serializers.PrimaryKeyRelatedField(
    queryset=Family.objects.all(),
    required=False,
    allow_null=True
)
    is_blocked = serializers.SerializerMethodField()
    password = serializers.CharField(required=False, write_only=True)
    confirm_password = serializers.CharField(required=False, write_only=True)

    # def get_family(self, obj):
    #     # ← skip family if we're already nested inside FamilySerializer
    #     if self.context.get('exclude_family'):
    #         return None
    #     from stages.serializers import FamilySerializer  # lazy import
    #     if obj.family is None:
    #         return None
    #     return FamilySerializer(obj.family, context=self.context).data

    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return AxesProxyHandler.is_locked(request, {'username': obj})

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'full_name',
            'password',
            'confirm_password',
            'address',     
            'phone',       
            'whatsapp',    
            'father',      
            'birth_date',  
            'joined_date', 
            'parent_phone',
            'role',
            'family',
            'image',
            'email',
            'last_login',
            'is_staff',
            'is_active',
            'is_blocked',
            'slogan',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        password = data.get("password")
        confirm = self.initial_data.get("confirm_password")

        if self.instance is None:
            if not password:
                raise serializers.ValidationError({
                    "password": "This field is required."
                })
            if password != confirm:
                raise serializers.ValidationError({
                    "confirm_password": "Passwords do not match."
                })
        else:
            if password and password != confirm:
                raise serializers.ValidationError({
                    "confirm_password": "Passwords do not match."
                })

        return data
    
    def validate_username(self, value):
        qs = CustomUser.objects.filter(username=value)
        # If editing, exclude the current instance from the check
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance