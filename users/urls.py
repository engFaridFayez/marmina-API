from django.urls import path

from users import views

from .custom_jwt_claims import CustomTokenObtainPairView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/', views.UsersList.as_view(), name='new_user'),
    path('me/', views.Me.as_view(), name='current_user'),
    path('users/user/<int:id>/', views.GetSingleUserView.as_view(), name='get-single-user'),
    path('users/new/', views.NewUserView.as_view(), name='new_user'),
    path('users/delete/', views.DeleteUserView.as_view(), name='delete_user'),
    path('users/update-user-status/', views.UpdateUserStatusView.as_view(), name='update-user-status'),
    path("users/update-me/", views.UpdateMyProfile.as_view()),
    path("admin/users/update/<int:user_id>/", views.AdminUpdateUser.as_view()),
    path("admin-reset-password/", views.AdminResetUserPassword.as_view(), name='admin-reset-password'),
    path('users/user-reset-password/', views.UserUpdatePassword.as_view(), name='user-reset-password'),
    path('users/change-user-role/', views.ManageUserRoles.as_view(), name='manage-user-role'),
    path('admin/change-stage-leader/',views.UpdateStageLeader.as_view())
]