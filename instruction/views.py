from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import InstructionsCreateSerializer
from .models import Instruction


class CreateInstructionsVies(generics.CreateAPIView):
    """
    This view should create new instruction
    for the user who have status admin
    """

    permission_classes = (IsAdminUser,)
    serializer_class = InstructionsCreateSerializer
    queryset = Instruction.objects.all()


class UDRInstructionsView(generics.RetrieveAPIView):
    """
    This view allows you to display a specific
    instruction for the currently authenticated user.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = InstructionsCreateSerializer
    queryset = Instruction.objects.all()
    lookup_field = 'name'


class DestroyInstructions(generics.DestroyAPIView):
    """
    This view allows you to  destroy a specific instruction
    for the currently authenticated user who have status admin.
    """
    permission_classes = (IsAdminUser,)
    serializer_class = InstructionsCreateSerializer
    queryset = Instruction.objects.all()
    lookup_field = 'name'


class UpdateInstructions(generics.UpdateAPIView):
    """
    This view allows you to  edit a specific instruction
    for the currently authenticated user who have status admin.
    """
    permission_classes = (IsAdminUser,)
    serializer_class = InstructionsCreateSerializer
    queryset = Instruction.objects.all()
    lookup_field = 'name'
