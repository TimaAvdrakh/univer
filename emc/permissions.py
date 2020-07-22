from rest_framework.permissions import BasePermission


class TeacherPermission(BasePermission):
    """
    Проверяет пользователя на роль преподавателя
    """
    message = 'У вас нет права доспута'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        return message for details
        """
        try:
            permission = request.user.profile.role.is_teacher
            return True if permission else False
        except AttributeError:
            return False
