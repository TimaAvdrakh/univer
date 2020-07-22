from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from organizations.models import TeacherDiscipline, StudentDiscipline
# from organizations.serializers import
from .serializers import EMCSerializer, TeacherDisciplineSerializer, StudentDisciplineSerializer
from .models import EMC
from .permissions import TeacherPermission


class EMCModelViewSet(ModelViewSet):
    serializer_class = EMCSerializer
    queryset = EMC.objects.all()

    @action(methods=['get'], detail=False, url_path='disciplines', url_name='disciplines')
    def get_disciplines(self, request, pk=None):
        """Получить список закрпеленных дисциплин в зависомости от роли (студента или учителя)
        """
        profile = self.request.user.profile
        is_student = profile.role.is_student
        is_teacher = profile.role.is_teacher
        if is_student:
            disciplines = StudentDiscipline.objects.filter(
                student=profile
            ).distinct('discipline').order_by('discipline__name')
            serializer = StudentDisciplineSerializer(disciplines, many=True).data
        elif is_teacher:
            disciplines = TeacherDiscipline.objects.filter(
                teacher=profile
            ).distinct('discipline').order_by('discipline__name')
            serializer = TeacherDisciplineSerializer(disciplines, many=True).data
        else:
            serializer = None
        return Response(serializer, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='', url_name='')
    def emc_filter(self, request, pk=None):
        qs = request.query_params
        qs.get('')
        return Response()

    @action(methods=['get'], detail=False, url_path='discipline', url_name='emc-discipline')
    def get_discipline(self, request, pk=None):
        discipline = request.query_params.get('discipline_uid')
        profile = self.request.user.profile
        is_student = profile.role.is_student
        is_teacher = profile.role.is_teacher
        if is_student:
            discipline = StudentDiscipline.objects.get(pk=discipline)
            serializer = StudentDisciplineSerializer(discipline).data
        elif is_teacher:
            discipline = TeacherDiscipline.objects.get(pk=discipline)
            serializer = TeacherDisciplineSerializer(discipline).data
        else:
            serializer = None
        return Response(data=serializer, status=status.HTTP_200_OK)


class CreateTeacherEMC(CreateAPIView):
    """
    Это представление создаёт УМК(учебно-методический комплекс)
    для авторизованного пользователя, с ролью преподавателя
    """
    serializer_class = EMCSerializer
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
