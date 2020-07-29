from rest_framework.permissions import BasePermission


class RetrieveUpdateDestroyPermission(BasePermission):

    def has_permission(self, request, view):
        """
        При 'GET' запросе выполняется проверка на аутентификацию,
        для остальных запросов требуется статус "is_staff".
        """
        if request.method == 'GET':
            return bool(request.user and request.user.is_authenticated)
        else:
            return bool(request.user and request.user.is_staff)
