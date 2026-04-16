import logging
from django.utils import timezone
from rest_framework import permissions , status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ValidationError
from axes.utils import reset
from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import ListAPIView , UpdateAPIView

from users.models import CustomUser
from users.serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)

class UsersList(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]


class UpdateUser(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]



class UpdateUserInfo(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self,request):
        data = request.data
        if self.checkif_request_field_valid(request,"username"):
            request.user.username = data["username"]
        if self.checkif_request_field_valid(request,"first_name"):
            request.user.first_name = data["first_name"]
        if self.checkif_request_field_valid(request,"last_name"):
            request.user.last_name = data["last_name"]
        if self.checkif_request_field_valid(request,"email"):
            request.user.email = data["email"]

        try:
            request.user.save()
        except Exception:
            error_message = CustomUser._meta.get_field('username').error_messages['unique']
            return Response({'error':error_message},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        return Response({"Updated!"},status=status.HTTP_200_OK)

    def checkif_request_field_valid(self,request,field_name):
        if field_name in request.data and request.data[field_name] and request.data[field_name] != "":
            return True
        return False
    

class DeactivateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def post(self,request):
        data = request.data
        user = CustomUser.objects.get(username=data['username'])
        if user.is_active == False:
            user.is_active = True
        else:
            user.is_active = False

        user.save()
        return Response({"User deactivated successfully"},status=200)
    
class UpdateUserStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self,request):
        data = request.data

        username = data['username']
        activity = data['status']

        user = CustomUser.objects.get(username=username)
        user.is_active = activity

        user.save()
        return Response({"Activity Updated"},status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated ,permissions.IsAdminUser]

    def delete(self,request,format=None):
        data = request.data
        user = CustomUser.objects.get(id=data['user_id'])
        user.delete()
        return Response({"message":"User deleted Successfully"},status=200)

class NewUserView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self,request):

        username = request.data.get("username")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if not confirm_password:
            return Response({"message":"Confirm password shouldn't be blank"},status=400)

        if password != confirm_password:
            return Response({"message":"Password and confirm pasword should be the same"},status=400)

        if not username:
            return Response({"message":"username must be provided"},status=400)
        if not password:
            return Response({"message":"password must be provided"},status=400)
        
        new_user = CustomUser.objects.create_user(
            username = username,
            password = password,
        )

        serializer = RegisterSerializer(new_user)

        return Response({"message":"User Created Successfully","user":serializer.data},status=200)

    
class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def delete(self,request,format=None):
        data = request.data
        user = CustomUser.objects.get(id=data['user_id'])
        user.delete()
        return Response({},status=200)
    
# class DeactivateUserView(APIView):
#     permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

#     def post(self,request):
#         data = request.data
#         user = User.objects.get(username=data['username'])
#         user.is_active = False
#         user.save()
#         return Response({"User has been deactivated successfully!"},status=status.HTTP_200_OK)
    


class ResetLoginView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def post(self,request):
        data = request.data
        if 'blocked_user' not in data.keys():
            raise ValidationError(detail={'blocked_user':'This field is required'})
        
        if not CustomUser.objects.filter(username=data['blocked_user']).exists():
            raise ValidationError(('username does not exist'),code='username does not exist')
        
        reset(username=data['blocked_user'])

        return Response({"User Unblocked"},status=status.HTTP_200_OK)
    

class AdminResetUserPassword(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def post(self,request):
        if not request.user.is_staff:
            return Response({'response':"User is not an admin"},status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        new_password = data['new_passwd']
        target_user = data['target_user']

        validate_password(new_password,target_user)
        user = CustomUser.objects.get(username=target_user)
        user.required_password_change = False
        user.password_change_date = timezone.now()
        user.set_password(new_password)
        user.save()

        return Response({'response':"Success!!!!!"},status=status.HTTP_200_OK)
    
class UserUpdatePassword(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        try:
            new_password = request.data.get('new_passwd')
            confirm_password = request.data.get('confirm_passwd')

        

            if new_password != confirm_password:
                raise ValidationError(("Password should match"),code = 'Password should match')
            user = request.user
            validate_password(new_password,user)
        except ValidationError as e:
            return Response({"errors":e.error_list},status=status.HTTP_403_FORBIDDEN)
        
        user.required_password_change = False
        user.password_change_date = timezone.now()
        user.set_password(new_password)
        user.save()

        return Response({'response':"Success!!!!!"},status=status.HTTP_200_OK)