from django.urls import path,include

from users import views

from .custom_jwt_claims import CustomTokenObtainPairView


from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('users/',views.UsersList.as_view(),name='new_user'),
    path('users/new/',views.NewUserView.as_view(),name='new_user'),
    path('token/',CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('users/delete/',views.DeleteUserView.as_view(),name='delete_user'),
    path('users/deactivate/',views.DeactivateUserView.as_view(),name='deactivate_user'),
    path('users/update-activity-status/',views.UpdateUserStatusView.as_view(),name='update_activity_status'),
    path('users/update-user-info/',views.UpdateUserInfo.as_view(),name='update_user_info'),
    path('users/admin-reset-login-attempts/',views.ResetLoginView.as_view(),name='unblock'),
    path('users/admin-reset-password/',views.AdminResetUserPassword.as_view(),name='admin-reset-password'),
    path('users/user-reset-password/',views.UserUpdatePassword.as_view(),name='user-reset-password')


]