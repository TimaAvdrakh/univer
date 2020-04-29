from django.shortcuts import render
from rest_framework import generics, views
from rest_framework import status
from rest_framework.response import Response
from . import serializers
from .models import *
import json

# Create your views here.
class TypeView(generics.ListAPIView):
    queryset = Type.objects.all()
    serializer_class = serializers.TypeSerializer

class SubTypeView(generics.ListAPIView):
    queryset = SubType.objects.all()
    serializer_class = serializers.SubTypeSerializer

    def get_queryset(self):
        application_type = self.request.query_params.get('application_type')
        queryset = self.queryset.filter()
        if application_type:
            queryset = self.queryset.filter(type_id=application_type)
        return queryset


class ApplicationView(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = serializers.ApplicationSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(profile=self.request.user.profile)
        return queryset

    def create(self, request, *args, **kwargs):
        data = json.loads(request.data["data"])

        request.data["profile"] = self.request.user.profile.uid
        request.data["type"] = data["type"]

        if request.data["identity_doc"] :
            request.data["identity_doc"] = IdentityDoc.objects.create(
                file=request.data["identity_doc"]
            )

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            sub_applications = data['subapplications']
            application = serializer.save()

            resp = {'message': 'ok', 'id': application.id}

            default_status = Status.objects.get(code=NEW)

            for sub in sub_applications:
                SubApplication.objects.create(
                    application=application,
                    subtype=SubType.objects.get(uid=sub['sub_type']),
                    organization=sub['org_name'],
                    is_paper=sub['is_paper'],
                    copies=sub['copy'],
                    lang=sub['lang'],
                    status=default_status
                )

            return Response(resp, status=status.HTTP_200_OK)
        else:
            return Response({'message': serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)
