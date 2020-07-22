from django.db.models import QuerySet

from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import EMCSerializer
from .models import EMC


class CreateEMC(CreateAPIView):
    """
    Это представление создаёт УМК(учебно-методический комплекс)
    для авторизованного пользователя, с ролью преподавателя
    """
    serializer_class = EMCSerializer
    permission_classes = (IsAuthenticated,)  # нужно добавить permission для преподавателя, который фильруется ролю


class ListEMC(ListAPIView):
    """
    Это представление выводит список УМК(учебно-методический комплекс)
    для авторизованного пользователя, с ролью студент
    """
    serializer_class = EMCSerializer
    permission_classes = (IsAuthenticated,)
    queryset = EMC.objects.all()

    # def get_queryset(self) -> QuerySet:
    #     user = self.request.user
    #     queryset = EMC.objects.filter(
    #         language__studentdiscipline__author=user  # нужно фильтровать с ролю студента
    #     )
    #
    #     return queryset
