from rest_framework import serializers
from organizations import models as org_models
from portal_users.serializers import ProfileShortSerializer, StudentDisciplineStatusSerializer, \
    ProfileForAdviserSerializer
from portal.curr_settings import student_discipline_info_status, student_discipline_status, not_choosing_load_types2
from cron_app.models import AdvisorRejectedBidTask
from . import models
from portal_users.utils import get_current_study_year
from common.exceptions import CustomException


class StudyPlanSerializer(serializers.ModelSerializer):
    education_program = serializers.CharField()
    student = ProfileShortSerializer()
    group = serializers.CharField()

    class Meta:
        model = org_models.StudyPlan
        fields = (
            'uid',
            'education_program',
            'student',
            'group',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['education_program_group'] = instance.education_program.group.code if instance.education_program.group else ' '  # instance.education_program.group.code
        data['loading'] = False
        data['error'] = False

        # Test
        study_year_id = self.context.get('study_year')
        status_id = self.context.get('status_id')
        acad_periods = self.context.get('acad_periods')

        disciplines_data = []

        if acad_periods is not None:
            acad_period_list = acad_periods.split(',')

            disciplines = org_models.StudentDiscipline.objects.filter(
                study_plan=instance,
                study_year_id=study_year_id,
                is_active=True,
            )

            if status_id:
                disciplines = disciplines.filter(status_id=status_id)

            for acad_period_id in acad_period_list:
                acad_period = org_models.AcadPeriod.objects.get(pk=acad_period_id)

                discipline_in_acad_per = disciplines.filter(acad_period=acad_period)\
                    .distinct('discipline').\
                    order_by('discipline')

                total_credit = sum(i.credit for i in discipline_in_acad_per)

                is_more = len(discipline_in_acad_per) > 3

                discipline_in_acad_per = discipline_in_acad_per[:3]
                serializer = StudentDisciplineShortSerializer(discipline_in_acad_per,
                                                              many=True)

                checks = models.AdvisorCheck.objects.filter(study_plan=instance,
                                                            acad_period=acad_period)

                if checks.exists():
                    old_status = checks.latest('id').status
                else:
                    old_status = 0

                resp = {
                    'total_credit': total_credit,
                    'disciplines': serializer.data,
                    'is_more': is_more,
                    'old_status': old_status,
                    'acad_period': acad_period.repr_name,
                    'uid': acad_period.uid,
                }
                disciplines_data.append(resp)
        data['acad_periods'] = disciplines_data
        # Test

        return data


class StudentDisciplineShortSerializer(serializers.ModelSerializer):
    """Используется для получения дисциплин студента для отчета Эдвайзеру (заявки на ИУПы)"""

    discipline = serializers.CharField(read_only=True)
    status = StudentDisciplineStatusSerializer()

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'discipline',
            'status',
            'hours',
            'author',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['credit'] = instance.credit
        data['acad_period'] = instance.acad_period.repr_name

        return data


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Faculty
        fields = (
            'uid',
            'name'
        )


class CathedraSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Cathedra
        fields = (
            'uid',
            'name'
        )


class GroupShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Group
        fields = (
            'uid',
            'name',
        )


class CheckStudentBidsSerializer(serializers.Serializer):
    """Эдвайзер утдерждает или отклоняет заявку на регистрации"""

    study_plan = serializers.PrimaryKeyRelatedField(
        queryset=org_models.StudyPlan.objects.filter(is_active=True),
    )
    acad_periods = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=org_models.AcadPeriod.objects.filter(is_active=True),
        )
    )
    status = serializers.IntegerField()
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Причина отклонения заявки студента',
    )
    study_year = serializers.PrimaryKeyRelatedField(
        queryset=org_models.StudyPeriod.objects.filter(is_study_year=True,
                                                       is_active=True)
    )
    status_check = serializers.BooleanField(default=False)

    def save(self, **kwargs):
        status_check = self.validated_data.pop('status_check')
        study_plan = self.validated_data.get('study_plan')
        acad_periods = self.validated_data.get('acad_periods')
        status = self.validated_data.get('status')
        comment = self.validated_data.get('comment')
        study_year = self.validated_data.get('study_year')

        if status == 4:  # Утвержден
            if not self.all_teacher_chosen(study_plan, acad_periods, study_year, status_check):
                raise CustomException(detail='not_all_chosen',
                                      status_code=200)

            info_status_id = student_discipline_info_status['confirmed']
            status_id = student_discipline_status['confirmed']
        elif status == 3:  # Отклонен
            info_status_id = student_discipline_info_status['rejected']
            status_id = student_discipline_status['rejected']
        else:
            raise CustomException(detail='not_valid_status')

        is_chosen = False
        for acad_period in acad_periods:
            try:
                student_discipline_info = org_models.StudentDisciplineInfo.objects.get(
                    study_plan=study_plan,
                    acad_period=acad_period
                )
            except org_models.StudentDisciplineInfo.DoesNotExist:
                continue

            student_discipline_info.status_id = info_status_id
            student_discipline_info.save()

            org_models.StudentDiscipline.objects.filter(
                study_plan=study_plan,
                acad_period=acad_period,
                is_active=True,
                teacher__isnull=False,  # TODO TEST
            ).update(status_id=status_id)

            models.AdvisorCheck.objects.create(
                study_plan=study_plan,
                status=status,
                acad_period=acad_period,
                comment=comment,
            )
            is_chosen = True

        if is_chosen and status == 3:  # Отклонен
            AdvisorRejectedBidTask.objects.create(  # Отправить письмо на емайл студента
                study_plan=study_plan,
                comment=comment,
            )

    def all_teacher_chosen(self, study_plan, acad_periods, study_year, status_check):
        """Проверим выбраны ли все преподы в указанных акад периодах"""
        if not status_check:
            invalid_statuses = [student_discipline_status['not_chosen'], student_discipline_status['rejected']]
        else:
            invalid_statuses = [student_discipline_status['not_chosen']]

        return not org_models.StudentDiscipline.objects.filter(
            study_plan=study_plan,
            acad_period__in=acad_periods,
            status__in=invalid_statuses,
            is_active=True,
            study_year=study_year,
        ).exclude(load_type__load_type2__in=not_choosing_load_types2).exists()


class StudyPlanDetailSerializer(serializers.ModelSerializer):
    student = serializers.CharField()
    study_period = serializers.CharField()
    group = serializers.CharField()
    speciality = serializers.CharField()
    faculty = serializers.CharField()
    cathedra = serializers.CharField()
    # education_program = EducationProgramSerializer()
    education_type = serializers.CharField()
    preparation_level = serializers.CharField()
    study_form = serializers.CharField()
    on_base = serializers.CharField()
    education_base = serializers.CharField()
    active = serializers.BooleanField(
        default=False,  # Для удобства на фронте
    )

    class Meta:
        model = org_models.StudyPlan
        fields = (
            'uid',
            'student',
            'study_period',
            'group',
            'speciality',
            'faculty',
            'cathedra',
            # 'education_program',
            'education_type',
            'preparation_level',
            'study_form',
            'on_base',
            'education_base',
            'active',
            'current_course',
            'entry_date',
        )

    def to_representation(self, instance):
        study_year_obj = self.context.get('study_year_obj')

        data = super().to_representation(instance)
        data['language'] = instance.group.language.name
        study_year_dict = get_current_study_year()
        data['current_study_year'] = '{}-{}'.format(study_year_dict['start'],
                                                    study_year_dict['end'])

        data['course'] = instance.get_course(study_year_obj)

        return data


class ConfirmedStudentDisciplineShortSerializer(serializers.ModelSerializer):
    """Используется в отчете для Эдвайзера"""

    discipline = serializers.CharField(read_only=True)

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'discipline',
            'discipline_code'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['credit'] = instance.credit

        if instance.component:
            data['component'] = instance.component.short_name
        elif instance.cycle:
            data['component'] = instance.cycle.short_name
        else:
            data['component'] = ''

        return data


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.Speciality
        fields = (
            'uid',
            'name',
            'code',
        )


class StudentDisciplineSerializer(serializers.ModelSerializer):
    """Используется в Результате регистрации"""

    discipline = serializers.CharField(read_only=True)
    load_type = serializers.CharField()
    language = serializers.CharField()
    teacher = serializers.CharField()
    student_count = serializers.IntegerField()

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'discipline',
            'load_type',
            'hours',
            'language',
            'teacher',
            'student_count',
        )


class RegisterStatisticsSerializer(serializers.Serializer):
    """Используется в Статистике Регистрации"""

    faculty = serializers.CharField()
    cathedra = serializers.CharField()
    speciality = serializers.CharField()
    group = serializers.CharField()
    student_count = serializers.IntegerField()
    discipline = serializers.CharField()
    not_chosen_student_count = serializers.IntegerField()
    percent_of_non_chosen_student = serializers.FloatField()


class NotRegisteredStudentSerializer(serializers.Serializer):
    """Используется в Списке незарегистрированных"""

    faculty = serializers.CharField()
    cathedra = serializers.CharField()
    speciality = serializers.CharField()
    group = serializers.CharField()
    discipline = serializers.CharField()
    student = serializers.CharField()

    # class Meta:
    #     model = org_models.StudentDiscipline
    #     fields = (
    #         'uid',
    #         'discipline',
    #     )
    #
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['faculty'] = instance.study_plan.faculty.name
    #     data['cathedra'] = instance.study_plan.cathedra.name
    #     data['speciality'] = instance.study_plan.speciality.name
    #     data['group'] = instance.study_plan.group.name
    #     data['student'] = instance.student.full_name
    #
    #     return data


class DeactivateDisciplineSerializer(serializers.ModelSerializer):
    """
    Деактивирует дисциплины студента
    """
    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
        )

    def update(self, instance, validated_data):
        org_models.StudentDiscipline.objects.filter(
            student=instance.student,
            discipline=instance.discipline,
            acad_period=instance.acad_period
        ).update(is_active=False)

        return instance


class ActivateDisciplineSerializer(serializers.ModelSerializer):
    """
    Деактивирует дисциплины студента
    """
    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
        )

    def update(self, instance, validated_data):
        org_models.StudentDiscipline.objects.filter(
            student=instance.student,
            discipline=instance.discipline,
            acad_period=instance.acad_period
        ).update(is_active=True)

        return instance


class StudentProfilesListSerializer(serializers.ModelSerializer):
    """
    Страница список всех студентов эдвайзера
    """
    student = ProfileForAdviserSerializer()

    class Meta:
        model = org_models.StudyPlan
        fields = (
            'student',
        )
