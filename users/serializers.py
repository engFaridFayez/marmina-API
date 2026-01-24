from rest_framework import serializers
from users.models import CustomUser
from axes.handlers.proxy import AxesProxyHandler

class UserSerializer(serializers.ModelSerializer):

    is_blocked = serializers.SerializerMethodField()

    def get_is_blocked(self,obj):
        request = self.context['request']
        return AxesProxyHandler.is_locked(request,{'username':obj})
    
    class Meta:

        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'last_login',
            'is_staff',
            'is_active',
            'required_password_change',
            'password_change_date',
            'is_blocked'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user