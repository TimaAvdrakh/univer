from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from organizations.models import TeacherDiscipline, StudentDiscipline, StudyPlan, AcadPeriod
from .serializers import (
    EMCSerializer, TeacherDisciplineSerializer, StudentDisciplineSerializer,
    StudyPlanSerializer, AcadSerializer
)
from .models import EMC
from .permissions import TeacherPermission
from .paginations import SmallResultSetPagination


class EMCModelViewSet(ModelViewSet):
    serializer_class = EMCSerializer
    queryset = EMC.objects.all()
    pagination_class = SmallResultSetPagination

    @action(methods=['get'], detail=False, url_path='study_plans', url_name='study_plans')
    def get_study_plans(self, request, pk=None):
        """Получить список УП студента"""

        profile = self.request.user.profile
        is_student = profile.role.is_student
        if is_student:
            study_plan = StudyPlan.objects.filter(
                student=profile,
            )
            acad_periods = AcadPeriod.objects.filter(
                acad_period__student=profile
            ).distinct('number')
            serializer_acad = AcadSerializer(acad_periods, many=True).data
            serializer_study = StudyPlanSerializer(study_plan, many=True).data
            return Response({"acad_periods": serializer_acad, "study_plan": serializer_study}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='disciplines', url_name='disciplines')
    def get_disciplines(self, request, pk=None):
        """Получить список закрпеленных дисциплин в зависомости от роли (студента или учителя)"""
        study_plan = request.query_params.get('study_plan_uid')
        acad_period = request.query_params.get('acad_period_uid')
        profile = self.request.user.profile
        is_student = profile.role.is_student
        is_teacher = profile.role.is_teacher
        if is_student:
            if study_plan and acad_period:
                disciplines = StudentDiscipline.objects.filter(
                    student=profile,
                    study_plan=study_plan,
                    acad_period=acad_period
                ).distinct('discipline__name').order_by('discipline__name')
                paginated_queryset = self.paginate_queryset(disciplines)
                return self.get_paginated_response(
                    StudentDisciplineSerializer(paginated_queryset, many=True).data
                )
            elif study_plan:
                disciplines = StudentDiscipline.objects.filter(
                    student=profile,
                    study_plan=study_plan,
                ).distinct('discipline__name').order_by('discipline__name')
                paginated_queryset = self.paginate_queryset(disciplines)
                return self.get_paginated_response(
                    StudentDisciplineSerializer(paginated_queryset, many=True).data
                )
            elif acad_period:
                disciplines = StudentDiscipline.objects.filter(
                    student=profile,
                    acad_period=acad_period
                ).distinct('discipline__name').order_by('discipline__name')
                paginated_queryset = self.paginate_queryset(disciplines)
                return self.get_paginated_response(
                    StudentDisciplineSerializer(paginated_queryset, many=True).data
                )
            else:
                disciplines = StudentDiscipline.objects.filter(
                    student=profile
                ).distinct('discipline__name').order_by('discipline__name')
                paginated_queryset = self.paginate_queryset(disciplines)
                return self.get_paginated_response(
                    StudentDisciplineSerializer(paginated_queryset, many=True).data
                )
        elif is_teacher:
            disciplines = TeacherDiscipline.objects.filter(
                teacher=profile
            ).distinct('discipline__name').order_by('discipline__name')
            paginated_queryset = self.paginate_queryset(disciplines)
            return self.get_paginated_response(
                TeacherDisciplineSerializer(paginated_queryset, many=True).data
            )
        else:
            serializer = None
            return Response(serializer, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='discipline', url_name='emc-discipline')
    def get_discipline(self, request, pk=None):
        """Получить список документов УМК по одной дисциплине в зависомости от роли (студента или учителя)"""
        discipline_uid = request.query_params.get('discipline_uid')
        profile = self.request.user.profile
        is_student = profile.role.is_student
        is_teacher = profile.role.is_teacher
        if is_student:
            student_discipline = StudentDiscipline.objects.get(pk=discipline_uid)
            emc_files = EMC.objects.filter(author=student_discipline.teacher.user,
                                           discipline__uid=student_discipline.discipline.uid)
            serializer = EMCSerializer(emc_files, many=True).data
        elif is_teacher:
            teacher_discipline = TeacherDiscipline.objects.get(pk=discipline_uid)
            emc_files = EMC.objects.filter(author=teacher_discipline.teacher.user,
                                           discipline__uid=teacher_discipline.discipline.uid)
            serializer = EMCSerializer(emc_files, many=True).data
        else:
            serializer = None
        return Response(data=serializer, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='discipline-one', url_name='emc-discipline-one')
    def get_discipline_one(self, request, pk=None):
        """Получить список УМК по одной дисциплине от всех преподавателей"""
        discipline = request.query_params.get('discipline')
        profile = self.request.user.profile
        is_teacher = profile.role.is_teacher
        if is_teacher:
            discipline = TeacherDiscipline.objects.filter(
                discipline=discipline
            ).distinct('discipline__name')
            serializer = TeacherDisciplineSerializer(discipline, many=True).data
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
