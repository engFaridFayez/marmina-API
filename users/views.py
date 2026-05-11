import logging
from rest_framework import permissions , status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import CustomUser
from users.serializers import ProfileSerializer, RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)

class UsersList(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = CustomUser.objects.select_related(
            'family',
            'family__stage'
        )

        if user.is_superuser or user.is_staff:
            # أدمن يشوف الكل
            pass

        elif user.role == "امين الشمامسة":
            # يشوف كل المستخدمين في كل المراحل
            pass  # مفيش فلتر — نفس الأدمن

        elif user.role == "امين مرحلة":
            # يشوف بس اللي في مرحلته
            queryset = queryset.filter(
                family__stage__leaders=user
            )

        elif user.family:
            # أمين أسرة أو خادم عادي — أسرته بس
            queryset = queryset.filter(family=user.family)

        else:
            # مفيش أسرة — يشوف نفسه بس
            queryset = queryset.filter(id=user.id)

        # فلتر اختياري بالأسرة
        family_id = self.request.query_params.get('family')
        if family_id:
            queryset = queryset.filter(family_id=family_id)

        return queryset.distinct()

class Me(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        serializer = ProfileSerializer(request.user,context={"request":request})
        return Response(serializer.data)

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
    permission_classes = [permissions.IsAuthenticated ,permissions.IsAdminUser]

    def delete(self,request,format=None):
        data = request.data
        user = CustomUser.objects.get(id=data['user_id'])
        user.delete()
        return Response({"message":"User deleted Successfully"},status=200)

class UpdateUserStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def post(self,request):
        data = request.data
        user = CustomUser.objects.get(username=data['username'])
        if user.is_active == False:
            user.is_active = True
        else:
            user.is_active = False

        user.save()
        return Response({"Message": f"user {user.username} is now {'active' if user.is_active else 'inactive'}",},status=200)
    
class UpdateMyProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self,request):
        user = request.user

        serializer = ProfileSerializer(
            user,
            data = request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "user": serializer.data
            }, status=200)
        
        return Response(serializer.errors, status=400)
class AdminUpdateUser(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]


    def patch(self,request,user_id):
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response({
                "error":"User Not Found"
            },status=status.HTTP_404_NOT_FOUND)
        
        data = request.data

        serializer = UserSerializer(
            user,
            data=data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "user": serializer.data
            }, status=200)
        
        return Response(serializer.errors, status=400)
class AdminResetUserPassword(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    def post(self,request):
        if not request.user.is_staff:
            return Response({'response':"User is not an admin"},status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        new_password = data['new_password']
        target_user = data['target_user']

        validate_password(new_password,target_user)
        user = CustomUser.objects.get(username=target_user)
        user.set_password(new_password)
        user.save()

        return Response({'response':"Password Changesd Successfully!"},status=status.HTTP_200_OK)

class UserUpdatePassword(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        try:
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            if new_password != confirm_password:
                raise ValidationError(("Password should match"),code = 'Password should match')
            user = request.user
            validate_password(new_password,user)
        except ValidationError as e:
            return Response({"errors":e.error_list},status=status.HTTP_403_FORBIDDEN)
        
        user.set_password(new_password)
        user.save()

        return Response({'response':"Password Changesd Successfully!"},status=status.HTTP_200_OK)
    


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
    









# ===========================================
#               OLD CODE
# ===========================================




#     class FamilyList(ListAPIView):
#     serializer_class = FamilySerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user

#         queryset = Family.objects.select_related('stage')

#         if user.is_superuser or user.is_staff:
#             return queryset

#         elif user.role == "امين الشمامسة":
#             # يشوف كل الأسر في كل المراحل
#             return queryset

#         elif user.role == "امين مرحلة":
#             return queryset.filter(
#                 stage__leaders=user
#             ).distinct()

#         elif user.family:
#             # خادم / أمين أسرة — أسرته بس
#             return queryset.filter(id=user.family.id)

#         return Family.objects.none()
# class FamilyViewSet(ModelViewSet):
#     queryset = Family.objects.all()
#     serializer_class = FamilySerializer

# class StageList(ListAPIView):
#     serializer_class = StageSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):

#         user = self.request.user

#         queryset = Stage.objects.prefetch_related(
#             'families',
#             'leaders'
#         )

#         # Admin
#         if user.is_superuser or user.is_staff:
#             return queryset

#         # أمين مرحلة
#         if user.role == "امين مرحلة":
#             return queryset.filter(
#                 leaders=user
#             )

#         # باقي المستخدمين
#         if user.family and user.family.stage:
#             return queryset.filter(
#                 id=user.family.stage.id
#             )

#         return Stage.objects.none()


# class UpdateUser(UpdateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

# class ResetLoginView(APIView):
#     permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

#     def post(self,request):
#         data = request.data
#         if 'blocked_user' not in data.keys():
#             raise ValidationError(detail={'blocked_user':'This field is required'})
        
#         if not CustomUser.objects.filter(username=data['blocked_user']).exists():
#             raise ValidationError(('username does not exist'),code='username does not exist')
        
#         reset(username=data['blocked_user'])

#         return Response({"User Unblocked"},status=status.HTTP_200_OK)
    

