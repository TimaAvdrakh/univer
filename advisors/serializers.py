from rest_framework import serializers
from organizations import models as org_models
from portal_users.serializers import ProfileShortSerializer, StudentDisciplineStatusSerializer
from portal.curr_settings import student_discipline_info_status, student_discipline_status


class StudyPlanSerializer(serializers.ModelSerializer):
    education_program = serializers.CharField()
    student = ProfileShortSerializer()

    class Meta:
        model = org_models.StudyPlan
        fields = (
            'education_program',
            'student',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['education_program_group'] = instance.education_program.group.name

        return data


class StudentDisciplineShortSerializer(serializers.ModelSerializer):
    """Используется для получения дисциплин студента для отчета Эдвайзеру (ИУП)"""

    discipline = serializers.CharField(read_only=True)
    status = StudentDisciplineStatusSerializer()

    class Meta:
        model = org_models.StudentDiscipline
        fields = (
            'uid',
            'discipline',
            'status',
            'hours',
        )


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

    def save(self, **kwargs):
        study_plan = self.validated_data.get('study_plan')
        acad_periods = self.validated_data.get('acad_periods')
        status = self.validated_data.get('status')

        if status == 4:  # Утвержден
            info_status_id = student_discipline_info_status['confirmed']
            status_id = student_discipline_status['confirmed']
        else:
            info_status_id = student_discipline_info_status['rejected']
            status_id = student_discipline_status['rejected']

        for acad_period in acad_periods:
            student_discipline_info = org_models.StudentDisciplineInfo.objects.get(
                study_plan=study_plan,
                acad_period=acad_period
            )
            student_discipline_info.status_id = info_status_id
            student_discipline_info.save()

            org_models.StudentDiscipline.objects.filter(
                study_plan=study_plan,
                acad_period=acad_period,
                is_active=True,
            ).update(status_id=status_id)


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
        data = super().to_representation(instance)
        data['language'] = instance.group.language.name

        return data
