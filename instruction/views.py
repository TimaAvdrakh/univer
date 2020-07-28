from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import InstructionsCreateSerializer
from .models import Instruction


class CreateInstructionsVies(generics.CreateAPIView):
    """
    Это представление даёт пользователю
    со статусов Админ создавать инструкции
    """

    permission_classes = (IsAdminUser,)
    serializer_class = InstructionsCreateSerializer


class InstructionsView(generics.RetrieveUpdateDestroyAPIView):
    """
    Это представление даёт пользователю со статусом Админ
    взять одну запись, редактировать его и удалять
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = InstructionsCreateSerializer
    queryset = Instruction.objects.all()
    lookup_field = 'name'

