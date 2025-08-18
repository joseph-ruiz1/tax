from rest_framework import permissions


class isOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view/edit
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
