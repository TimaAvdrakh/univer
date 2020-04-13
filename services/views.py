from django.shortcuts import render
from rest_framework import generics, views
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from . import models
import json

# Create your views here.
class TypeView(generics.ListAPIView):
    queryset = models.Type.objects.all().order_by('-id')
    serializer_class = serializers.TypeSerializer