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

# Create your views here.
class SubTypeView(generics.ListAPIView):
    queryset = models.SubType.objects.all()
    serializer_class = serializers.SubTypeSerializer

    def get_queryset(self):
        type = self.request.query_params.get('service_type')
        queryset = self.queryset.filter()
        if type:
            queryset = self.queryset.filter(type_id=type)
        return queryset