import logging
from rest_framework import permissions , status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from auditlogging.services.logging import log_action
from stages.models import Stage
from users.models import CustomUser, StageLeader
from users.permissions import AllExceptServant, IsHead
from users.serializers import ProfileSerializer, UserSerializer
from rest_framework.generics import RetrieveAPIView

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

class GetSingleUserView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

class NewUserView(APIView):
    permission_classes = [AllExceptServant]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            log_action(
                actor=request.user,
                action="block",
                message=f"{request.user.full_name} created {user.full_name}",
                target_user=user
            )

            return Response({
                "message": "User Created Successfully",
                "user": UserSerializer(user).data
            }, status=201)

        return Response(serializer.errors, status=400)
class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated ,permissions.IsAdminUser]

    def delete(self,request,format=None):
        data = request.data
        user = CustomUser.objects.get(id=data['user_id'])
        user.delete()
        return Response({"message":"User deleted Successfully"},status=200)

class UpdateUserStatusView(APIView):
    permission_classes = [AllExceptServant]

    def post(self,request):
        data = request.data
        message = ""
        user = CustomUser.objects.get(pk=data['id'])
        if user.is_active == False:
            user.is_active = True
            message = f"{request.user.full_name} unblocked {user.full_name}"
        else:
            user.is_active = False
            message = f"{request.user.full_name} blocked {user.full_name}"

        user.save()
        
        log_action(
            actor=request.user,
            action="block",
            message=message,
            target_user=user
        )
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
    permission_classes = [AllExceptServant]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, user_id):
        print("REQUEST DATA:", request.data)
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User Not Found"},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()

        stage_id = data.pop("stage_id", None)

        serializer = UserSerializer(
            user,
            data=data,
            partial=True
        )

        if not serializer.is_valid():
            print("VALIDATED DATA:", serializer.validated_data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        if stage_id is not None:

            # إزالة المستخدم من أي مرحلة قديمة
            user.managed_stages.clear()

            # إضافة المستخدم للمرحلة الجديدة
            if stage_id:
                try:
                    stage = Stage.objects.get(id=stage_id)
                except Stage.DoesNotExist:
                    return Response(
                        {"error": "Stage Not Found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                stage.leaders.add(user)

        log_action(
            actor=request.user,
            action="update",
            message=f"{request.user.full_name} updated {user.full_name}",
            target_user=user
        )
        print("SERIALIZER ERRORS:", serializer.errors)
        return Response(
            {
                "message": "User updated successfully",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )

class AdminResetUserPassword(APIView):
    permission_classes = [AllExceptServant]

    def post(self, request):
        target_user_id = request.data.get("target_user")
        new_password = request.data.get("new_password")

        if not target_user_id or not new_password:
            return Response(
                {"response": "Missing data"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(pk=target_user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"response": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            validate_password(new_password, user)
            log_action(
                actor=request.user,
                action="update",
                message=f"{request.user.full_name} change the password for {user.full_name}",
                target_user=user
            )
        except Exception as e:
            return Response(
                {"response": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"response": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
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
    


class UpdateStageLeader(APIView):
    permission_classes = [IsHead,permissions.IsAdminUser]

    def patch(self,request):
        user = request.user
        stage_id = request.data.get("stage")
        leader_id = request.data.get("leader")
        
        if not stage_id or not leader_id:
            return Response(
                {"error": "stage and leader are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            stage = Stage.objects.get(id=stage_id)
            leader = CustomUser.objects.get(id=leader_id)
        except Stage.DoesNotExist:
            return Response({"error": "Stage not found"}, status=404)
        except CustomUser.DoesNotExist:
            return Response({"error": "Leader not found"}, status=404)
        
        obj, created = StageLeader.objects.update_or_create(
            stage = stage,
            defaults={"customuser":leader}
        )
        return Response({
            "message": "Leader updated successfully"
        })






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
    

