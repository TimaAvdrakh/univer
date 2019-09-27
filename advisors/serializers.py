from rest_framework import serializers
from organizations import models as org_models
from portal_users.serializers import ProfileShortSerializer, StudentDisciplineStatusSerializer


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
