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
from rest_framework.parsers import MultiPartParser, FormParser

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

class Me(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        serializer = UserSerializer(request.user,context={"request":request})
        return Response(serializer.data)

class UpdateMyProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self,request):
        print("USER:", request.user)
        print("TYPE:", type(request.user))
        user = request.user
        data = request.data

        if "username" in data:
            user.username = data["username"]

        if "first_name" in data:
            user.first_name = data["first_name"]

        if "last_name" in data:
            user.last_name = data["last_name"]

        if "email" in data:
            user.email = data["email"]

        if "image" in request.FILES:
            user.image = request.FILES["image"]

        try:
            user.save()
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "message": "Profile updated successfully",
            "user": {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "image": user.image.url if user.image else None,
            }
        }, status=status.HTTP_200_OK)
    
class AdminUpdateUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self,request,user_id):
        if not request.user.is_staff:
            return Response(
                {"error": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response({
                "error":"User Not Found"
            },status=status.HTTP_404_NOT_FOUND)
        
        data = request.data

        if "username" in data:
            user.username = data["username"]

        if "first_name" in data:
            user.first_name = data["first_name"]

        if "last_name" in data:
            user.last_name = data["last_name"]

        if "email" in data:
            user.email = data["email"]

        if "role" in data:
            user.role = data["role"]

        if "image" in request.FILES:
            user.image = request.FILES["image"]

        user.save()

        return Response({
            "message": "User updated by admin",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            }
        }, status=status.HTTP_200_OK)
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
        
        user.set_password(new_password)
        user.save()

        return Response({'response':"Success!!!!!"},status=status.HTTP_200_OK)
    

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
        user.set_password(new_password)
        user.save()

        return Response({'response':"Success!!!!!"},status=status.HTTP_200_OK)
    
class ManageUserRoles(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        new_role = request.data.get('role')
        target_username = request.data.get('user')

        # 🔴 Validation: البيانات موجودة؟
        if not new_role or not target_username:
            return Response(
                {'error': 'role and user are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔴 Validation: المستخدم موجود؟
        try:
            user = CustomUser.objects.get(username=target_username)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔴 Validation: الرول صح؟
        valid_roles = [choice[0] for choice in CustomUser._meta.get_field('role').choices]

        if new_role not in valid_roles:
            return Response(
                {
                    'error': 'Invalid role',
                    'valid_roles': valid_roles
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔴 (اختياري) منع تغيير نفسك مثلاً
        # لو مش عايز اليوزر يغير رول نفسه:
        if request.user.username == target_username:
            return Response(
                {'error': 'You cannot change your own role'},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ تحديث الرول
        user.role = new_role
        user.save()

        return Response(
            {'message': 'Role updated successfully'},
            status=status.HTTP_200_OK
        )