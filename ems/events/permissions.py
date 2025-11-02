from rest_framework import permissions

class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # read allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user

class IsInvitedOrPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        if obj.organizer == request.user:
            return True
        return request.user in obj.invited_users.all()
