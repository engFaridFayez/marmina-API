from rest_framework import serializers
from users.models import CustomUser
from axes.handlers.proxy import AxesProxyHandler


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

    is_blocked = serializers.SerializerMethodField()
    password = serializers.CharField(required=False, write_only=True)
    confirm_password = serializers.CharField(required=False, write_only=True)
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
            'confirm_password', 
            'last_login',
            'is_staff',
            'is_active',
            'required_password_change',
            'password_change_date',
            'is_blocked'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        password = data.get("password")
        confirm = self.initial_data.get("confirm_password")

        # 🟢 Create
        if self.instance is None:
            if not password:
                raise serializers.ValidationError({
                    "password": "This field is required."
                })
            if password != confirm:
                raise serializers.ValidationError({
                    "confirm_password": "Passwords do not match."
                })

        # 🟡 Update
        else:
            if password and password != confirm:
                raise serializers.ValidationError({
                    "confirm_password": "Passwords do not match."
                })
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        products = validated_data.pop('products', None)

        # update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # update password (optional)
        if password:
            instance.set_password(password)

        instance.save()

        # update products only if sent
        if products is not None:
            instance.products.set(products)

        return instance
        