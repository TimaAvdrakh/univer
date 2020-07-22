from rest_framework import serializers
from .models import Instruction


class InstructionsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ('name', 'file', 'language')
