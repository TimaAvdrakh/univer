from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned
from base64 import b64decode
import json
from common import models as models_common
from organizations import models as models_organizations
from portal_users import models as models_portal_users
from schedules import models as models_schedules
from applications import models as models_applications
# from portal.curr_settings import journal_statuses
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from . import serializers
import requests
from django.contrib.auth.models import User
from cron_app.models import CredentialsEmailTask
from uuid import uuid4
from rest_framework.views import APIView

from .models import *
from django.views.decorators.csrf import csrf_exempt
from portal.local_settings import DELETE_RECORDS_API_TOKEN
from portal.curr_settings import student_discipline_status
from django.db import connection


@csrf_exempt
def putfrom1c(request):
    # if not request.user.is_superuser:
    #     return HttpResponse('Forbidden')

    if request.POST['token'] != 'lsdfgflg45454adsa5d645':
        return HttpResponse('Forbidden')

    if request.method == 'POST':
        rules = cache.get('rule1c')
        if rules is None:
            rules = []
            qs = C1Object.objects.filter(is_active=True)
            for item in qs:
                fields = []

                for field in item.c1objectcompare_set.all():
                    fields.append(
                        {
                            'c1': field.c1,  # Поле 1С
                            'django': field.django,  # Поле Django
                            'main_field': field.main_field,  # Ведущее поле
                            'is_binary_data': field.is_binary_data
                        })

                rules.append(
                    {
                        'object': item.name,  # Ключ словаря
                        'model': item.model,  # Имя модели
                        'is_related': item.is_related,
                        'fields': fields  # Поля модели
                    })
                # cache.set('rule1c', rules)

        stri = request.POST['structure']
        stri = stri.replace('muachuille', ';')
        stri = stri.replace('huyachuille', '&')
        d = json.loads(stri)  # Словарь
        has_not_saved = False
        for each in d:
            current_rule = None
            for rule in rules:
                if rule['object'] == each:
                    current_rule = rule
                    break

            if current_rule is None:
                continue

            current_list = d[each]
            cnt = 0
            Manager = eval('models_' + current_rule['model'])  # Model

            # if current_rule['is_related']:
            # for p in Manager.objects.all():
            #     p.delete()

            for each_elem in current_list:
                q = {}
                if current_rule['is_related']:
                    """Связанная модель"""

                    for each in current_rule['fields']:
                        if Manager._meta.get_field(each['django']).unique:  # TODO ???
                            q[each['django']] = each_elem[each['c1']]

                    if len(q):
                        try:
                            finding_object = Manager.objects.get(**q)
                            finding_object.exchange = True  # TODO реализовать в Дисциплине
                        except Manager.DoesNotExist:
                            finding_object = Manager()
                            finding_object.exchange = True
                        except MultipleObjectsReturned:
                            print(q, 'MultipleObjectsReturned: ' + str(cnt + 1) + current_rule['model'])
                            continue
                    else:
                        try:
                            ut = Manager._meta.unique_together
                            for i in ut[0]:
                                for rule_field in current_rule['fields']:
                                    if str(i) + '_id' == rule_field['django']:
                                        if each_elem[rule_field['c1']] == '00000000-0000-0000-0000-000000000000':
                                            q[str(i) + '_id'] = None
                                        else:
                                            q[str(i) + '_id'] = each_elem[rule_field['c1']]
                                    elif str(i) == rule_field['django']:
                                        q[str(i)] = each_elem[rule_field['c1']]

                            finding_object = Manager.objects.get(**q)
                            finding_object.exchange = True
                        except Manager.DoesNotExist:
                            finding_object = Manager()
                            finding_object.exchange = True
                        except MultipleObjectsReturned:
                            print(q, 'MultipleObjectsReturned: ' + str(cnt + 1) + current_rule['model'])
                            continue
                else:
                    """Не связанная модель"""
                    try:
                        finding_object = Manager.objects.get(uid=each_elem[u'uid'])
                        finding_object.exchange = True
                    except:
                        finding_object = Manager()
                        finding_object.exchange = True
                        # if not current_rule['is_related']:
                        finding_object.uid = each_elem[u'uid']

                for rule_field in current_rule['fields']:
                    value = each_elem[rule_field['c1']]
                    if value == '00000000-0000-0000-0000-000000000000':
                        value = None

                    finding_field = getattr(finding_object,
                                            rule_field['django'])

                    if type(finding_field) == bool and value is None:
                        value = False

                    if type(finding_field) == str and value is None:
                        value = ''

                    if (type(finding_field) == int or type(
                            finding_field) == float) and value is None:  # or type(finding_field) == long
                        value = 0

                    is_related = False
                    if str(type(
                            finding_field)) == "<class 'django.db.models.fields.related_descriptors.ManyRelatedManager'>":
                        finding_field.clear()
                        is_related = True
                        for each_inserted in value:
                            try:
                                finding_field.add(each_inserted[rule_field['many_to_many_field']])
                            except:
                                finding_object.save()
                                finding_field.add(each_inserted[rule_field['many_to_many_field']])

                    if rule_field['is_binary_data']:
                        base64_string = value  # .encode('utf-8')
                        # data_index = base64_string.index('base64') + 7
                        # filedata = base64_string[data_index:len(base64_string)]
                        image = b64decode(base64_string)

                        setattr(
                            finding_object,
                            rule_field['django'],
                            ContentFile(image, each_elem['uid'] + '.jpg')
                        )

                    if not is_related and not rule_field['is_binary_data']:
                        try:
                            setattr(
                                finding_object,
                                rule_field['django'],
                                value
                            )
                        except Exception as ex:
                            print(ex)
                try:
                    finding_object.save()
                except Exception as ex:
                    print(str(cnt + 1) + " " + current_rule['model'] + " wasn't save.")
                    print(ex)
                cnt = cnt + 1
            print(str(cnt) + ' ' + current_rule['model'])

        if has_not_saved:
            return HttpResponse('not_saved')
        else:
            cache.set('main_tree', None)
            # models.GoodGroup.objects.rebuild()
            return HttpResponse('ok')


# def create_electronic_journals():
#     """Создаем электронные журналы после загрузки Занятии"""
#     flow_uids = models_schedules.Lesson.objects.filter(is_active=True).distinct('flow_uid').values('flow_uid')
#
#     for flow in flow_uids:
#         lessons = models_schedules.Lesson.objects.filter(flow_uid=flow['flow_uid'])
#         first_lesson = lessons.first()
#         ej = models_schedules.ElectronicJournal.objects.create(
#             flow_uid=flow['flow_uid'],
#             discipline=first_lesson.discipline,
#             load_type=first_lesson.load_type,
#             study_year=first_lesson.study_year,
#         )
#         # ej.teachers.set(first_lesson.teachers.filter(is_active=True))
#
#         for lesson in lessons:
#             lesson.el_journal = ej
#             lesson.save()


class C1ObjectView(generics.ListAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = serializers.C1ObjectSerializer
    queryset = C1Object.objects.all()


class C1ObjectCompareView(generics.ListAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = serializers.C1ObjectCompareSerializer
    queryset = C1ObjectCompare.objects.all()


class CopyRuleView(generics.RetrieveAPIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        resp = requests.get(url='http://kabinet.kazatu.kz:2050/api/v1/c1/c1_objects/')
        if resp.status_code == 200:
            c1_objects = resp.json()  # json.loads(resp.content)

            for item in c1_objects:
                try:
                    obj = C1Object.objects.get(pk=item['uid'])
                    obj.name = item['name']
                    obj.model = item['model']
                    obj.is_related = item['is_related']

                except C1Object.DoesNotExist:
                    C1Object.objects.create(
                        uid=item['uid'],
                        name=item['name'],
                        model=item['model'],
                        is_related=item['is_related'],
                    )

        resp = requests.get(url='http://apiuniver.cskz.kz/api/v1/c1/c1_object_compares/')
        if resp.status_code == 200:
            c1_object_compares = resp.json()  # json.loads(resp.content)

            for item in c1_object_compares:
                try:
                    obj = C1ObjectCompare.objects.get(pk=item['uid'])
                    obj.name = item['name']
                    obj.c1_object_id = item['c1_object']
                    obj.c1 = item['c1']
                    obj.django = item['django']
                    obj.main_field = item['main_field']
                    obj.is_binary_data = item['is_binary_data']

                except C1ObjectCompare.DoesNotExist:
                    C1ObjectCompare.objects.create(
                        uid=item['uid'],
                        name=item['name'],
                        c1_object_id=item['c1_object'],
                        c1=item['c1'],
                        django=item['django'],
                        main_field=item['main_field'],
                        is_binary_data=item['is_binary_data'],
                    )

        return Response(
            {
                'message': 'ok'
            },
            status=status.HTTP_200_OK,
        )


# class LoadAvatarView(generics.CreateAPIView):
#     def create(self, request, *args, **kwargs):
#         if request.data['token'] != 'lsdfgflg45454adsa5d645':
#             return Response(
#                 {
#                     'message': 'forbidden'
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#
#         resp = []
#         data = request.data['data']
#         for item in data:
#             d = {
#                 'uid': item['uid'],
#                 'code': 0,
#             }
#             try:
#                 profile = models_portal_users.Profile.objects.get(uid=item['uid'])
#             except models_portal_users.Profile.DoesNotExist:
#                 d['code'] = 1
#                 resp.append(d)
#                 continue
#
#             image = b64decode(item['avatar'])
#             content_f = ContentFile(image)
#             image_name = '{}.jpg'.format(uuid4())
#             profile.avatar.save(image_name, content_f)
#             resp.append(d)
#
#         return Response(
#             resp,
#             status=status.HTTP_200_OK
#         )


@csrf_exempt
def deactivate_obj(request):
    """Удалить объект"""
    if request.method == 'POST':
        if request.POST['token'] != DELETE_RECORDS_API_TOKEN:
            return HttpResponse('Forbidden')

        stri = request.POST['structure']
        stri = stri.replace('muachuille', ';')
        stri = stri.replace('huyachuille', '&')
        d = json.loads(stri)  # Словарь

        resp = []  # [{'profiles': ['uid1', 'uid2']}]

        for model_name, val_list in d.items():
            try:
                c1_obj = C1Object.objects.get(name=model_name,
                                              is_active=True)
            except C1Object.DoesNotExist:
                return JsonResponse(
                    {
                        'message': 'model_not_found'
                    },
                    status=404
                )

            Manager = eval('models_' + c1_obj.model)  # Model
            resp_elems = []

            for val in val_list:
                try:
                    obj = Manager.objects.get(uuid1c=val['uuid1c'])
                    obj.is_active = val['is_active']
                    obj.save()
                    resp_elems.append(val)
                except Manager.DoesNotExist:
                    pass

            resp_model = {
                model_name: resp_elems,
            }
            resp.append(resp_model)

        # try:
        #     to_resp = resp.pop()
        # except IndexError:
        #     to_resp = {
        #         'message': 'error',
        #     }
        return JsonResponse(
            resp,
            safe=False,
            status=200,
        )


@csrf_exempt
def putfrom1c_copy(request):
    """Измененый вариант, отправляет в ответе успешные сохраненные записи"""

    if request.POST['token'] != 'lsdfgflg45454adsa5d645':
        return HttpResponse('Forbidden')

    if request.method == 'POST':
        rules = cache.get('rule1c')
        if rules is None:
            rules = []
            qs = C1Object.objects.filter(is_active=True)
            for item in qs:
                fields = []

                for field in item.c1objectcompare_set.all():
                    fields.append(
                        {
                            'c1': field.c1,  # Поле 1С
                            'django': field.django,  # Поле Django
                            'main_field': field.main_field,  # Ведущее поле
                            'is_binary_data': field.is_binary_data
                        })

                rules.append(
                    {
                        'object': item.name,  # Ключ словаря
                        'model': item.model,  # Имя модели
                        'is_related': item.is_related,
                        'fields': fields  # Поля модели
                    })
                # cache.set('rule1c', rules)

        stri = request.POST['structure']
        stri = stri.replace('muachuille', ';')
        stri = stri.replace('huyachuille', '&')
        d = json.loads(stri)  # Словарь
        has_not_saved = False

        resp = []  # [{'profiles': ['uid1', 'uid2']}]

        to_resp = {}

        for each in d:
            current_rule = None
            for rule in rules:
                if rule['object'] == each:
                    current_rule = rule
                    break

            if current_rule is None:
                continue

            current_list = d[each]
            cnt = 0
            Manager = eval('models_' + current_rule['model'])  # Model

            # if current_rule['is_related']:
            # for p in Manager.objects.all():
            #     p.delete()

            resp_elems = []

            for each_elem in current_list:
                q = {}
                if current_rule['is_related']:
                    """Связанная модель"""

                    for each_field in current_rule['fields']:
                        if Manager._meta.get_field(each_field['django']).unique:  # TODO ???
                            q[each_field['django']] = each_elem[each_field['c1']]

                    if len(q):
                        try:
                            finding_object = Manager.objects.get(**q)
                            finding_object.exchange = True  # TODO реализовать в Дисциплине
                        except Manager.DoesNotExist:
                            finding_object = Manager()
                            finding_object.exchange = True
                        except MultipleObjectsReturned:
                            print(q, 'MultipleObjectsReturned: ' + str(cnt + 1) + current_rule['model'])
                            continue
                    else:
                        try:
                            ut = Manager._meta.unique_together
                            for i in ut[0]:
                                for rule_field in current_rule['fields']:
                                    if str(i) + '_id' == rule_field['django']:
                                        if each_elem[rule_field['c1']] == '00000000-0000-0000-0000-000000000000':
                                            q[str(i) + '_id'] = None
                                        else:
                                            q[str(i) + '_id'] = each_elem[rule_field['c1']]
                                    elif str(i) == rule_field['django']:
                                        q[str(i)] = each_elem[rule_field['c1']]

                            finding_object = Manager.objects.get(**q)
                            finding_object.exchange = True
                        except Manager.DoesNotExist:
                            finding_object = Manager()
                            finding_object.exchange = True
                        except MultipleObjectsReturned:
                            print(q, 'MultipleObjectsReturned: ' + str(cnt + 1) + current_rule['model'])
                            continue
                else:
                    """Не связанная модель"""
                    try:
                        finding_object = Manager.objects.get(uid=each_elem[u'uid'])
                        finding_object.exchange = True
                    except:
                        finding_object = Manager()
                        finding_object.exchange = True
                        # if not current_rule['is_related']:
                        finding_object.uid = each_elem[u'uid']

                for rule_field in current_rule['fields']:
                    value = each_elem[rule_field['c1']]
                    if value == '00000000-0000-0000-0000-000000000000':
                        value = None

                    finding_field = getattr(finding_object,
                                            rule_field['django'])

                    if type(finding_field) == bool and value is None:
                        value = False

                    if type(finding_field) == str and value is None:
                        value = ''

                    if (type(finding_field) == int or type(
                            finding_field) == float) and value is None:  # or type(finding_field) == long
                        value = 0

                    is_related = False
                    if str(type(
                            finding_field)) == "<class 'django.db.models.fields.related_descriptors.ManyRelatedManager'>":
                        finding_field.clear()
                        is_related = True
                        for each_inserted in value:
                            try:
                                finding_field.add(each_inserted[rule_field['many_to_many_field']])
                            except:
                                finding_object.save()
                                finding_field.add(each_inserted[rule_field['many_to_many_field']])

                    if rule_field['is_binary_data']:
                        base64_string = value  # .encode('utf-8')
                        # data_index = base64_string.index('base64') + 7
                        # filedata = base64_string[data_index:len(base64_string)]

                        base64_string = base64_string.replace(" ", "+")
                        image = b64decode(base64_string)

                        if rule_field['django'][-3:] == "_id":
                            ff = finding_object._meta.get_field(rule_field['django'][:-3]).remote_field.model
                            new_file = ff.objects.create(file=ContentFile(image, each_elem['uid'] + each_elem['extension']))
                            setattr(finding_object, rule_field['django'], new_file.id)
                        else:
                            setattr(
                                finding_object,
                                rule_field['django'],
                                ContentFile(image, each_elem['uid'] + each_elem['extension'])
                                # ContentFile(image, each_elem['uid'] + '.jpg')
                            )

                    if not is_related and not rule_field['is_binary_data']:
                        try:
                            setattr(
                                finding_object,
                                rule_field['django'],
                                value
                            )
                        except Exception as ex:
                            print(ex)
                try:
                    finding_object.save()
                    resp_elems.append(each_elem)  # TODO проверять!
                except Exception as ex:
                    print(str(cnt + 1) + " " + current_rule['model'] + " wasn't save.")
                    print(ex)
                cnt = cnt + 1
            print(str(cnt) + ' ' + current_rule['model'])

            resp_model = {
                each: resp_elems,
            }
            resp.append(resp_model)
            try:
                to_resp = resp.pop()
            except IndexError:
                to_resp = {
                    'message': 'error',
                }

        if has_not_saved:
            return HttpResponse('not_saved')
        else:
            cache.set('main_tree', None)
            # models.GoodGroup.objects.rebuild()
            # return HttpResponse('ok')
            return JsonResponse(
                to_resp,
                status=200
            )


# class ClearRecordWithoutUidView(generics.RetrieveAPIView):
#     def get(self, request, *args, **kwargs):
#         # if not request.user.is_superuser:
#         #     return Response(
#         #         {
#         #             'message': 'forbidden'
#         #         },
#         #         status=status.HTTP_400_BAD_REQUEST
#         #     )
#
#         tds = models_organizations.TeacherDiscipline.objects.filter(uuid1c='')
#         for td in tds:
#             td.delete()
#
#         # sds = models_organizations.StudentDiscipline.objects.filter(uuid1c='')
#         # for sd in sds:
#         #     sd.delete()
#
#         # pres = models_organizations.Prerequisite.objects.filter(uuid1c='')
#         # for pre in pres:
#         #     pre.delete()
#
#         # posts = models_organizations.Postrequisite.objects.filter(uuid1c='')
#         # for post in posts:
#         #     post.delete()
#
#         return Response(
#             {
#                 'message': 'ok'
#             },
#             status=status.HTTP_400_BAD_REQUEST
#         )


class FindDuplicateView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        sds = models_organizations.StudentDiscipline.objects.filter(uuid1c='')
        for sd in sds:
            print(sd.uid)
            # print('UID 1C:', sd.uuid1c)
            sd.uuid1c = None
            sd.save()
            # print('UID 1C:', sd.uuid1c)
            # print('\n')

        print('To null. ok')

        return Response(
            {
                'messag': 'ok'
            },
            status=status.HTTP_200_OK
        )

        # query = '''
        #                 SELECT sd.student_id, sd.study_plan_uid_1c, sd.acad_period_id,
        #                        sd.discipline_code, sd.discipline_id,
        #                        sd.load_type_id, sd.hours, sd.cycle_id, sd.study_year_id,
        #                        COUNT(*) AS dup_count
        #                 FROM organizations_studentdiscipline sd
        #                 WHERE sd.study_year_id = 'c4f1122b-31f5-11e9-aa40-0cc47a2bc1bf'
        #                 GROUP BY sd.student_id, sd.study_plan_uid_1c, sd.acad_period_id,
        #                          sd.discipline_code, sd.discipline_id,
        #                          sd.load_type_id, sd.hours, sd.cycle_id, sd.study_year_id
        #                 HAVING COUNT(*) > 1
        #             '''
        #
        # with connection.cursor() as cursor:
        #     cursor.execute(query)
        #
        #     rows = cursor.fetchall()
        #
        # for item in rows:
        #     sds = models_organizations.StudentDiscipline.objects.filter(
        #         student=item[0],
        #         study_plan_uid_1c=item[1],
        #         acad_period=item[2],
        #         discipline_code=item[3],
        #         discipline=item[4],
        #         load_type=item[5],
        #         hours=item[6],
        #         cycle=item[7],
        #         study_year=item[8],
        #     )
        #     print('Dup_num: ', item[9])
        #     if len(sds) > 1:
        #         # print('Duplicate: {}-{}-{}-{}-{}-{}-{}-{}-{}'.format(
        #         #     sds[0].student.user.username,
        #         #     sds[0].study_plan_uid_1c,
        #         #     sds[0].acad_period.name,
        #         #     sds[0].discipline.name,
        #         #     sds[0].discipline_code,
        #         #     sds[0].load_type.name,
        #         #     sds[0].hours,
        #         #     sds[0].cycle.name,
        #         #     sds[0].study_year.repr_name,
        #         # ))
        #
        #         uuid1c = None
        #         for sd in sds:
        #             if sd.uuid1c is not None:
        #                 uuid1c = sd.uuid1c
        #
        #         confirmed_sds = sds.filter(status_id=student_discipline_status['confirmed'])
        #         if len(confirmed_sds) > 0:
        #             for i, each in enumerate(confirmed_sds):
        #                 if i == 0:
        #                     each.uuid1c = uuid1c
        #                     each.save()
        #                 else:
        #                     each.delete()
        #             sds.exclude(status_id=student_discipline_status['confirmed']).delete()
        #
        #         else:
        #             for i, each in enumerate(sds):
        #                 if i == 0:
        #                     each.uuid1c = uuid1c
        #                     each.save()
        #                 else:
        #                     each.delete()
        #
        # return Response(
        #     {
        #         'messag': 'ok'
        #     },
        #     status=status.HTTP_200_OK
        # )

        # sds = org_models.StudentDiscipline.objects.filter(
        #     study_year_id='c4f1122b-31f5-11e9-aa40-0cc47a2bc1bf',
        #     uuid1c__isnull=True,
        # )
        # for sd in sds:
        #     print(sd.uid)
        #     sd.delete()
        #
        # print('no uid delete. ok')
        #
        # return Response(
        #     {
        #         'messag': 'ok'
        #     },
        #     status=status.HTTP_200_OK
        # )
