from django.shortcuts import render
from rest_framework import generics, views
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from . import models
import json

# Create your views here.
class TypeView(generics.ListAPIView):
    queryset = models.Type.objects.all()
    serializer_class = serializers.TypeSerializer

class SubTypeView(generics.ListAPIView):
    queryset = models.SubType.objects.all()
    serializer_class = serializers.SubTypeSerializer

    def get_queryset(self):
        type = self.request.query_params.get('application_type')
        queryset = self.queryset.filter()
        if type:
            queryset = self.queryset.filter(type_id=type)
        return queryset


class ApplicationView(generics.ListCreateAPIView):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationSerializer

    def create(self, request, *args, **kwargs):
        user = request.user

        request.data["status"] = models.Status.objects.filter(c1_id="1").first().uid
        request.data["type"] = request.data["type"]["uid"]
        request.data["profile"] = self.request.user.profile.uid

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            return Response({'message': 1}, status=status.HTTP_200_OK)
        else:
            return Response({'message': serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)
