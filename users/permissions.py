from rest_framework import permissions

class IsHead(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "امين الشمامسة"
    
class IsStageLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "امين مرحلة"
    
class IsFamilyLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "امين اسرة"
    
class IsServant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "خادم عادي"

class AllExceptServant(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["امين اسرة", "امين مرحلة", "امين الشمامسة"]
        )


class CanManageResults(permissions.BasePermission):

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        # Django Admin / Superuser
        if request.user.is_superuser:
            return True

        # المستخدم لازم يكون خادم/مسؤول
        return request.user.role == "خادم"