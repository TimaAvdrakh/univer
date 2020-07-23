from rest_framework import serializers
from common.models import File, ReservedUID
from common.serializers import FileSerializer
from organizations.models import TeacherDiscipline, StudentDiscipline
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
        emc: EMC = super().create(validated_data)
        # TODO договориться с фронтовиком насчет field_name в File
        files = File.objects.filter(gen_uid=ReservedUID.get_uid_by_user(user), field_name=None)
        emc.files.set(files)
        emc.save()
        return emc


class DisciplineSerializer(serializers.ModelSerializer):
    discipline_name = serializers.SerializerMethodField(read_only=True)
    emcs = serializers.SerializerMethodField(read_only=True)


class TeacherDisciplineSerializer(DisciplineSerializer):
    def get_emcs(self, td: TeacherDiscipline):
        discipline = td.discipline
        emcs = discipline.emcs.all()
        return EMCSerializer(emcs, many=True).data

    def get_discipline_name(self, td: TeacherDiscipline):
        return td.discipline.name

    class Meta:
        model = TeacherDiscipline
        fields = '__all__'


class StudentDisciplineSerializer(DisciplineSerializer):

    def get_emcs(self, td: TeacherDiscipline):
        discipline = td.discipline
        emcs = discipline.emcs.all()
        return EMCSerializer(emcs, many=True).data

    def get_discipline_name(self, sd: StudentDiscipline):
        return sd.discipline.name

    class Meta:
        model = StudentDiscipline
        fields = '__all__'
