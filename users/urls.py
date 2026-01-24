from django.urls import path,include

from .custom_jwt_claims import CustomTokenObtainPairView

from users.views import AdminResetUserPassword, DeactivateUserView, DeleteUserView, ResetLoginView, UpdateUserInfo, UpdateUserStatusView, UserUpdatePassword, UsersView, NewUserView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users',UsersView)

urlpatterns = [
    path('', include(router.urls)),

    path('users/new',NewUserView.as_view(),name='new_user'),
    path('token/',CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('users/delete',DeleteUserView.as_view(),name='delete_user'),
    path('users/deactivate',DeactivateUserView.as_view(),name='deactivate_user'),
    path('users/update-activity-status',UpdateUserStatusView.as_view(),name='update_activity_status'),
    path('users/update-user-info',UpdateUserInfo.as_view(),name='update_user_info'),
    path('users/admin-reset-login-attempts',ResetLoginView.as_view(),name='unblock'),
    path('users/admin-reset-password',AdminResetUserPassword.as_view(),name='admin-reset-password'),
    path('users/user-reset-password',UserUpdatePassword.as_view(),name='user-reset-password')


]