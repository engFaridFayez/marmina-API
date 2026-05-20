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