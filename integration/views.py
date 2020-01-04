from rest_framework import generics
from . import serializers
from rest_framework.response import Response
from rest_framework import status
from portal.curr_settings import G1_SOFT_AUTH_KEY


class StudentPresenceView(generics.CreateAPIView):
    """
    for G1 Soft
    auth_key - токен авторизации
    user - ИИН студента
    aud - Уид аудитории
    time - timestamp
    """
    serializer_class = serializers.StudentPresenceSerializer
    permission_classes = ()
    authentication_classes = ()

    def create(self, request, *args, **kwargs):
        token = request._request.headers['Token']

        if token != G1_SOFT_AUTH_KEY:
            return Response(
                {
                    'message': 'auth_key_invalid'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.serializer_class(data=request.data,
                                           many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.resp,
            status=status.HTTP_200_OK
        )
