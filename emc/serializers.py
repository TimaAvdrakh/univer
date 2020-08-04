from rest_framework import serializers
from common.models import File, ReservedUID
from common.serializers import FileSerializer
from organizations.models import TeacherDiscipline, StudentDiscipline, StudyPlan, AcadPeriod, Language
from .models import EMC


class EMCSerializer(serializers.ModelSerializer):
    discipline_name = serializers.SerializerMethodField(read_only=True)
    language_name = serializers.SerializerMethodField(read_only=True)
    files = FileSerializer(many=True, read_only=True)
    author_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EMC
        fields = '__all__'

    def get_discipline_name(self, emc: EMC):
        return emc.discipline.name

    def get_language_name(self, emc: EMC):
        return emc.language.name

    def get_author_name(self, emc: EMC):
        try:
            return emc.author.profile.full_name
        except:
            return emc.author.username

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        # 1. Сохраняем УМК
        emc: EMC = super().create(validated_data)
        # 2. Тащим файлы, загруженные в текущей модалке/форме
        files = File.objects.filter(gen_uid=ReservedUID.get_uid_by_user(user), field_name=emc.discipline.pk)
        emc.files.set(files)
        emc.save()
        # Деактивируем UID пользователя, чтобы при заливании новых файлов, не вышли старые со старым UID'ом
        ReservedUID.deactivate(user)
        return emc


class DisciplineSerializer(serializers.ModelSerializer):
    discipline_name = serializers.SerializerMethodField(read_only=True)
    emcs = serializers.SerializerMethodField(read_only=True)
    teacher_name = serializers.SerializerMethodField(read_only=True)

    def get_discipline_name(self, td: TeacherDiscipline):
        return td.discipline.name

    def get_emcs(self, td: TeacherDiscipline):
        discipline = td.discipline
        emcs = discipline.emcs.all()
        return EMCSerializer(emcs, many=True).data

    def get_teacher_name(self, td: TeacherDiscipline):
        try:
            return td.teacher.full_name
        except:
            return None


class TeacherDisciplineSerializer(DisciplineSerializer):
    class Meta:
        model = TeacherDiscipline
        fields = '__all__'


class StudentDisciplineSerializer(DisciplineSerializer):
    class Meta:
        model = StudentDiscipline
        fields = '__all__'


class StudyPlanSerializer(serializers.ModelSerializer):
    # student_disciplines = serializers.SerializerMethodField(read_only=True)
    #
    # def get_student_disciplines(self, sp: StudyPlan):
    #     student_disciplines = sp.study_plan.all()
    #     return StudentDisciplineSerializer(student_disciplines, many=True).data

    class Meta:
        model = StudyPlan
        fields = '__all__'


class AcadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcadPeriod
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class AcadPeriodAndStudyPlan(serializers.Serializer):
    acad = AcadSerializer(many=True)
    study_plan = StudyPlanSerializer(many=True)

    class Meta:
        fields = ['acad', 'study_plan']
