from django.urls import path,include

from users import views

from .custom_jwt_claims import CustomTokenObtainPairView


from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'families', views.FamilyViewSet, basename='families')


urlpatterns = [
    path('users/', views.UsersList.as_view(), name='new_user'),
    path('me/', views.Me.as_view(), name='current_user'),
    path('users/new/', views.NewUserView.as_view(), name='new_user'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/delete/', views.DeleteUserView.as_view(), name='delete_user'),
    path('users/deactivate/', views.DeactivateUserView.as_view(), name='deactivate_user'),
    path('users/update-activity-status/', views.UpdateUserStatusView.as_view(), name='update_activity_status'),
    path("users/update-me/", views.UpdateMyProfile.as_view()),
    path("admin/users/<int:user_id>/", views.AdminUpdateUser.as_view()),
    path('users/admin-reset-login-attempts/', views.ResetLoginView.as_view(), name='unblock'),
    path('users/admin-reset-password/', views.AdminResetUserPassword.as_view(), name='admin-reset-password'),
    path('users/user-reset-password/', views.UserUpdatePassword.as_view(), name='user-reset-password'),
    path('users/change-user-role/', views.ManageUserRoles.as_view(), name='manage-user-role'),

    path('stages/', views.StageList.as_view(), name='stages-list'),

    # ❌ القديم (لو مش محتاجه شيله)
    # path('families/', views.FamilyList.as_view(), name='families-list'),

    # ✅ الجديد
    path('', include(router.urls)),
]