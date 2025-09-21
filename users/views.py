import logging
from django.utils import timezone
from rest_framework import permissions , status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

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

    def put(self,request,format=None,*args,**kwargs):
        data = request.data
        user = User.objects.get(id=kwargs['id'],username=data['username'],first_name=data['firstName'],last_name=data['lastName'],email=data['email'])
        status = 201
        try:
            user.save()
        except Exception:
            error_message = User._meta.get_field('username').error_messages['unique']
            status = 406
            return Response({'error':error_message},status=status)
        return Response({'User Updated!'},status=200)

class NewUserView(APIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self,request, format=None):
        data = request.data
        user = User(username=data['username'],first_name=data['firstName'],last_name=data['lastName'],email=data['email'],is_staff=data['is_staff'],is_active=True,required_password_change=True,password_change_date=timezone.now())
        user.set_password(data['passwd'])
        status = 201
        try:
            status = user.save()
        except Exception:
            error_message = User._meta.get_field('username').error_messages['unique']
            status = 406
            return Response({'error':error_message},status=status)
        
        return Response({"User Created Successfully!!"},status=status)
    
class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def delete(self,request,format=None):
        data = request.data
        user = User.objects.get(id=data['user_id'])
        user.delete()
        return Response({},status=200)
    
class DeactivateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def post(self,request):
        data = request.data
        user = User.objects.get(username=data['username'])
        user.is_active = False
        user.save()
        return Response({"User has been deactivated successfully!"},status=status.HTTP_200_OK)
    
class UpdateUserStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def post(self,request):
        data = request.data
        username = data['username']
        activity = data['activity']

        user = User.objects.get(username=username)
        user.is_active = activity
        user.save()
        return Response({"Activity updated"},status=status.HTTP_200_OK)
