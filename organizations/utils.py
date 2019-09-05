from django.conf import settings
from modeltranslation.manager import get_translatable_fields_for_model
from rest_framework import serializers


class TranslatedModelSerializerMixin(serializers.ModelSerializer):
    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        trans_fields = get_translatable_fields_for_model(self.Meta.model)
        all_fields = []

        requested_langs = []
        if 'request' in self.context:
            lang_param = self.context['request'].query_params.get('lang', None)
            requested_langs = lang_param.split(',') if lang_param else []

        for f in fields:
            if f not in trans_fields:
                all_fields.append(f)
            else:
                for l in settings.LANGUAGES:
                    if not requested_langs or l[0] in requested_langs:
                        all_fields.append("{}_{}".format(f, l[0]))

        return all_fields
