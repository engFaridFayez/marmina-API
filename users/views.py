import logging
from django.utils import timezone
from rest_framework import permissions , status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ValidationError
from axes.utils import reset
from django.contrib.auth.password_validation import validate_password

from users.models import User
from users.serializers import UserSerializer

logger = logging.getLogger(__name__)

class UsersView(ModelViewSet):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    paginator = None

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
            error_message = User._meta.get_field('username').error_messages['unique']
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
        user = User.objects.get(username=data['username'])
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

        user = User.objects.get(username=username)
        user.is_active = activity

        user.save()
        return Response({"Activity Updated"},status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated ,permissions.IsAdminUser]

    def delete(self,request,format=None):
        data = request.data
        user = User.objects.get(id=data['user_id'])
        user.delete()
        return Response({"message":"User deleted Successfully"},status=200)

class NewUserView(APIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self,request, format=None):
        data = request.data
        user = User(username=data['username'],first_name=data['firstName'],last_name=data['lastName'],email=data['email'],is_staff=data['is_staff'],is_active=True,required_password_change=True,password_change_date=timezone.now())
        user.set_password(data['passwd'])
        try:
            validate_password(data['passwd'],user)
            user.save()
        except ValidationError as e:
            return Response(e,status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            error_message = User._meta.get_field('username').error_messages['unique']
            return Response({'error':error_message},status=status.HTTP_406_NOT_ACCEPTABLE)
        
        return Response({"User Created Successfully!!"},status=status.HTTP_200_OK)
    
class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def delete(self,request,format=None):
        data = request.data
        user = User.objects.get(id=data['user_id'])
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
        
        if not User.objects.filter(username=data['blocked_user']).exists():
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
        user = User.objects.get(username=target_user)
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