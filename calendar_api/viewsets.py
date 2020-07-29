from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q, prefetch_related_objects
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet
from common.paginators import CustomPagination
from portal_users.models import (
    Profile,
    RoleNames,
    Role,
    RoleNamesRelated,
)
from schedules.models import (
    Room,
    RoomType,
    Lesson,
    LessonStudent,
    LessonTeacher,
)
from univer_admin.permissions import IsAdminOrReadOnly, AdminPermission
from organizations.models import (
    StudyPlan,
    Group,
    Faculty,
    Cathedra,
    EducationProgram,
    EducationProgramGroup
)
from . import models
from . import serializers
from . import permissions


def lookup_and_filtration(group=None, faculty=None, cathedra=None, edu_program=None, edu_program_group=None):
    lookup = Q()
    if group is not None:
        lookup = lookup & Q(group=group)
    if faculty is not None:
        lookup = lookup & Q(faculty=faculty)
    if cathedra is not None:
        lookup = lookup & Q(cathedra=cathedra)
    if edu_program is not None:
        lookup = lookup & Q(education_program=edu_program)
    if edu_program_group is not None:
        lookup = lookup & Q(education_progra__group=edu_program_group)
    return lookup


class EventsViewSet(ModelViewSet):
    queryset = models.Events.objects.all()
    serializer_class = serializers.EventSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def list(self, request):
        queryset = self.queryset.filter(creator=self.request.user.profile).order_by('event_start')
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True).data
        paginated_response = self.get_paginated_response(serializer)
        return Response(data=paginated_response.data, status=HTTP_200_OK)

    @action(methods=['get',], detail=False, url_path='supervisor_students', url_name='supervisor_students')
    def get_supervisor_students(self, request, pk=None):
        queryset = StudyPlan.objects.filter(advisor=request.user.profile).order_by('group','student__last_name')
        page = self.paginate_queryset(queryset)
        serializer = serializers.SupervisorStudentsViewSerializer(page, many=True).data
        paginated_response = self.get_paginated_response(serializer)
        return Response(data=paginated_response.data, status=HTTP_200_OK)

    @action(methods=['get',], detail=False, url_path='student_events', url_name='student_events')
    def get_student_events(self, request, pk=None):
        if request.user.profile.role.is_supervisor:
            student_uid = request.query_params.get('uid', None)
            try:
                study_plan = StudyPlan.objects.filter(student=student_uid).first()
                lookup = Q(creator=student_uid)
                lookup |= Q(participants__participant_profiles=student_uid)
                lookup |= Q(participants__group=study_plan.group)
                lookup |= Q(participants__faculty=study_plan.faculty)
                lookup |= Q(participants__cathedra=study_plan.cathedra)
                lookup |= Q(participants__education_programs=study_plan.education_program)
                # lookup |= Q(participants__education_program_groups=study_plan.education_program.group)
                events = models.Events.objects.filter(lookup).distinct()
                serializer = serializers.EventSerializer(events, many=True).data
                return Response(data=serializer, status=HTTP_200_OK)
            except StudyPlan.DoesNotExist:
                return Response(data="Does not exist", status=HTTP_200_OK)
        else:
            raise PermissionError({"error": "You don't have rights to this data"})


class EventsRepetitionTypeViewSet(ModelViewSet):
    queryset = models.RepetitionTypes.objects.all()
    serializer_class = serializers.EventsRepetitionTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ReserveRoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = serializers.ReserveRoomSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def list(self, request):
        queryset = self.queryset
        event_start = request.query_params.get("event_start")
        event_end = request.query_params.get("event_end")
        room_type = request.query_params.get("room_type", None)
        department = request.query_params.get("department", None)

        room_name = request.query_params.get("room_name", None)

        if event_start is None or event_end is None:
            raise ValidationError({"error": "date_not_given"})
        lookup = Q()

        if room_name is not None:
            lookup = Q(name__contains=room_name)
        if room_type is not None:
            lookup = lookup & Q(type=room_type)
        if department is not None:
            lookup = lookup & Q(department=department)

        queryset = queryset.filter(lookup)
        context = {
            "event_start": event_start,
            "event_end": event_end,
        }
        serializer_data = self.serializer_class(queryset, many=True, context=context)
        return Response(data=serializer_data.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_name='room_type', url_path='room_type')
    def get_room_type(self, request, pk=None):
        room_type_queryset = RoomType.objects.filter(is_active=True)
        serializer = serializers.RoomTypeSerializer(room_type_queryset, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)


class ProfileChooseViewSet(ModelViewSet):
    queryset = Profile.objects.filter(is_active=True)
    serializer_class = serializers.ProfilesEventsSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination

    @action(methods=['get'], detail=False, url_name='profiles', url_path='profiles')
    def get_profiles(self, request, pk=None):
        event_start = request.query_params.get("event_start", None)
        event_end = request.query_params.get("event_end", None)
        if event_start is None or event_end is None:
            raise ValidationError({"error": "event_start and event_end query params required"})

        group = request.query_params.get("group", None)
        faculty = request.query_params.get("faculty", None)
        cathedra = request.query_params.get("cathedra", None)
        edu_program = request.query_params.get("education_program", None)
        edu_program_group = request.query_params.get("education_program_group", None)

        role = request.query_params.get("role", None)

        full_name = request.query_params.get('full_name', None)

        lookup = Q()

        if full_name is not None:
            lookup = Q(first_name__contains=full_name)
            lookup |= Q(last_name__contains=full_name)
            lookup |= Q(middle_name__contains=full_name)

        study_plans = StudyPlan.objects.filter(lookup_and_filtration(
            group, faculty, cathedra, edu_program, edu_program_group
        )).values_list('student')

        queryset = self.queryset.filter(lookup)

        if study_plans.exists():
            queryset = queryset.filter(pk__in=study_plans)
        if role is not None:
            profiles_from_role_related = RoleNamesRelated.objects.filter(role_name=role).values_list('profile')
            queryset = queryset.filter(pk__in=profiles_from_role_related)

        paginated_queryset = self.paginate_queryset(queryset)

        context = {
            "event_start": self.request.query_params.get("event_start"),
            "event_end": self.request.query_params.get("event_end")
        }

        serializer = self.serializer_class(paginated_queryset, many=True, context=context).data
        paginated_response = self.get_paginated_response(serializer)

        return Response(data=paginated_response.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='groups', url_name='groups')
    def get_groups(self, request, pk=None):
        faculty = request.query_params.get("faculty", None)
        cathedra = request.query_params.get('cathedra', None)
        edu_program = request.query_params.get("education_program", None)
        edu_program_group = request.query_params.get("education_program_group", None)
        queryset = StudyPlan.objects.filter(lookup_and_filtration(
            faculty=faculty,
            cathedra=cathedra,
            edu_program=edu_program,
            edu_program_group=edu_program_group,
        )).values_list('group', flat=True).distinct()
        groups_queryset = Group.objects.filter(pk__in=queryset, is_active=True).order_by('name')
        serializer = serializers.GroupEventSerializer(groups_queryset, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_name='cathedra', url_path='cathedra')
    def get_cathedra(self, request, pk=None):
        faculty = request.query_params.get('faculty')
        queryset = self.queryset.filter(lookup_and_filtration(faculty=faculty)).values_list('cathedra').distinct()
        cathedra_queryset = Cathedra.objects.filter(pk__in=queryset, is_active=True).order_by('name')
        serializer = serializers.CathedraEventSerializer(cathedra_queryset, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_name='faculty', url_path='faculty')
    def get_faculty(self, request, pk=None):
        faculty_queryset = Faculty.objects.filter(is_active=True).order_by('name')
        serializer = serializers.FacultyEventSerializer(faculty_queryset, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_name='edu_program', url_path='edu_program')
    def get_education_program(self, request, pk=None):
        edu_program_group = request.query_params.get('education_program_group', None)
        lookup = Q()
        if edu_program_group is not None:
            lookup = Q(education_program__group=edu_program_group)
        edu_program_queryset = EducationProgram.objects.filter(lookup, is_active=True).order_by('name')
        serializer = serializers.EducationProgramEventSerializer(edu_program_queryset, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='edu_program_group', url_name='edu_program_group')
    def get_education_program_group(self, request, pk=None):
        edu_program_group_queryset = EducationProgramGroup.objects.filter(is_active=True).order_by('name')
        serializer = serializers.EducationProgramGroupEventSerializer(
            edu_program_group_queryset,
            many=True
        )
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='role_names', url_name='role_names')
    def get_role_names(self, request, pk=None):
        role_names = RoleNames.objects.filter(is_active=True).order_by('name')
        serializer = serializers.RolenNamesSerializer(role_names, many=True).data
        return Response(data=serializer, status=HTTP_200_OK)


class ScheduleViewSet(ModelViewSet):
    queryset = Lesson.objects.filter(is_active=True)
    serializer_class = serializers.ScheduleSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def list(self, request):
        queryset = self.queryset
        profile = request.user.profile
        if not profile.role.is_student and not profile.role.is_teacher:
            return Response(data=[], status=HTTP_200_OK)
        if profile.role.is_student:
            all_lessons = LessonStudent.objects.filter(
                is_active=True,
                student=profile
            ).values_list('flow_uid')
            queryset = queryset.filter(flow_uid__in=all_lessons)
        if profile.role.is_teacher:
            queryset = queryset.filter(teachers=profile)
        queryset = queryset.order_by('date', 'time')
        serializer = self.serializer_class(queryset, many=True).data
        return Response(data=serializer, status=HTTP_200_OK)
