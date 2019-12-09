from django.shortcuts import HttpResponse
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned
from base64 import b64decode
import json
from common import models as models_common
from organizations import models as models_organizations
from portal_users import models as models_portal_users
from schedules import models as models_schedules
from portal.curr_settings import journal_statuses


from .models import *
# import cmartsite.models as models
from django.views.decorators.csrf import csrf_exempt


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
            qs = C1Object.objects.all()
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

                    if (type(finding_field) == int or type(finding_field) == float) and value is None:  # or type(finding_field) == long
                        value = 0

                    is_related = False
                    if str(type(finding_field)) == "<class 'django.db.models.fields.related_descriptors.ManyRelatedManager'>":
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


def create_electronic_journals():
    """Создаем электронные журналы после загрузки Занятии"""
    flow_uids = models_schedules.Lesson.objects.filter(is_active=True).distinct('flow_uid').values('flow_uid')

    for flow in flow_uids:
        lessons = models_schedules.Lesson.objects.filter(flow_uid=flow['flow_uid'])
        first_lesson = lessons.first()
        ej = models_schedules.ElectronicJournal.objects.create(
            flow_uid=flow['flow_uid'],
            discipline=first_lesson.discipline,
            load_type=first_lesson.load_type,
        )
        ej.teachers.set(first_lesson.teachers.filter(is_active=True))

        for lesson in lessons:
            lesson.el_journal = ej
            lesson.save()
