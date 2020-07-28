from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response

from .serializers import InstructionsCreateSerializer
from .models import Instruction
from .permissions import RetrieveUpdateDestroyPermission


class CreateInstructionsVies(generics.CreateAPIView):
    """
    Это представление даёт пользователю
    со статусов Админ создавать инструкции
    """

    permission_classes = (IsAdminUser,)
    serializer_class = InstructionsCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        cd = serializer.validated_data
        if cd:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(
                {"error": "instruction с таким name уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class InstructionsView(generics.RetrieveUpdateDestroyAPIView):
    """
    Это представление даёт пользователю со статусом Админ
    взять одну запись, редактировать его и удалять
    """

    permission_classes = (RetrieveUpdateDestroyPermission,)
    serializer_class = InstructionsCreateSerializer
    queryset = Instruction.objects.all()
    lookup_field = 'name'

    def get(self, request, name, *args, **kwargs):
        queryset = Instruction.objects.filter(name=name)
        if queryset:
            return self.retrieve(request, *args, **kwargs)
        else:
            return Response(
                {"error": "Не найдено инструкция под таким именем."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=False)
        cd = serializer.validated_data
        if cd:
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response(
                {"error": "Это поле не может быть пустым."},
                status=status.HTTP_400_BAD_REQUEST,
            )
