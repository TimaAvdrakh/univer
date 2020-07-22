from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView
)

from .serializers import EMCSerializer, EMCCreateSerializer
from .models import EMC
from .permissions import TeacherPermission


class CreateTeacherEMC(CreateAPIView):
    """
    Это представление создаёт УМК(учебно-методический комплекс)
    для авторизованного пользователя, с ролью преподавателя
    """
    serializer_class = EMCCreateSerializer
    permission_classes = (TeacherPermission,)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)


class EMCListOneTeacher(ListAPIView):
    """
    Это представление отображает УМК(учебно-методический комплекс)
    преподавателя по его дисциплинам
    """
    serializer_class = EMCSerializer
    permission_classes = (TeacherPermission,)

    def get_queryset(self) -> EMC:
        user = self.request.user
        queryset = EMC.objects.filter(
            author=user
        )

        return queryset


class EMCListTeacherByDiscipline(ListAPIView):
    """
    Это представление отображает УМК(учебно-методический комплекс)
    преподавателей по одной дисциплине
    """
    serializer_class = EMCSerializer
    permission_classes = (TeacherPermission,)

    def get_queryset(self) -> EMC:
        name = self.kwargs["discipline"]
        queryset = EMC.objects.filter(
            discipline__name=name
        )

        return queryset


class ListStudentEMC(ListAPIView):
    """
    Это представление выводит список УМК(учебно-методический комплекс)
    для авторизованного пользователя, с ролью студент
    """
    serializer_class = EMCSerializer

    queryset = EMC.objects.all()

    # def get_queryset(self) -> EMC:
    #     user = self.request.user
    #     queryset = EMC.objects.filter(
    #
    #     )
    #
    #     return queryset
