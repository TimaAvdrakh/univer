from django.shortcuts import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned
from base64 import b64decode
import pytz, json, shutil
from common import models as models_common
from cmart.settings import TIME_ZONE, CACHES
from .models import *
from datetime import datetime, timedelta
import cmartsite.models as models


def logon1c(request):
    user = authenticate(username=request.POST['login'].lower(),
                        password=request.POST['password'])
    if user != None:
        login(request, user)
        request.session.set_expiry(1209600)
        return HttpResponse('0')
    return HttpResponse('1')


@csrf_exempt
def putpicturefrom1c(request):
    if request.user.is_superuser:
        file = ContentFile(request.body, request.GET['good'])
        good = models.Good.objects.get(pk=request.GET['good'])
        good.picture = file
        good.save()
        file.close()
    return HttpResponse('ok')


@csrf_exempt
def putactfrom1c(request):
    if request.user.is_superuser:
        file = ContentFile(request.body, request.GET['uid'] + '.pdf')
        kontragent = models.Kontragent.objects.get(pk=request.GET['uid'])
        kontragent.reconciliation = file
        kontragent.save()
        file.close()
    return HttpResponse('ok')


@csrf_exempt
def putfilefrom1c(request):
    if request.user.is_superuser:
        file = ContentFile(request.body, request.GET['uid'] + '.' + request.GET['ext'])
        c1object = C1Object.objects.get(name=request.GET['model'])
        Manager = eval('models_' + c1object.model)
        instance = Manager.objects.get(uid=request.GET['uid'])
        field = c1object.c1objectcompare_set.get(c1=request.GET['field']).django

        setattr(instance, field, file)
        instance.save()
        file.close()
    return HttpResponse('ok')


@csrf_exempt
def putcountfrom1c(request):
    if request.user.is_superuser:
        file = ContentFile(request.body, request.GET['uid'] + '.pdf')
        order = models.Order.objects.get(pk=request.GET['uid'])
        order.account = file
        order.save()
        file.close()
    return HttpResponse('ok')


def putfrom1c(request):
    # user = authenticate(username='admin', password='Qu3TkAO6lB8V3Mlx')
    # login(request, user)
    if not request.user.is_superuser:
        return HttpResponse('Forbidden')

    if request.method == 'POST':
        rules = cache.get('rule1c')
        if rules == None:
            rules = []
            qs = C1Object.objects.all()
            for item in qs:
                fields = []

                for field in item.c1objectcompare_set.all():
                    fields.append(
                        {
                            'c1': field.c1,
                            'django': field.django,
                            'main_field': field.main_field,
                            'is_binary_data': field.is_binary_data
                        })

                rules.append(
                    {
                        'object': item.name,
                        'model': item.model,
                        'is_related': item.is_related,
                        'fields': fields
                    })
                # cache.set('rule1c',rules)
        stri = request.POST['structure']
        stri = stri.replace('muachuille', ';')
        stri = stri.replace('huyachuille', '&')
        d = json.loads(stri)
        has_not_saved = False
        for each in d:
            current_rule = None
            for rule in rules:
                if rule['object'] == each:
                    current_rule = rule
                    break
            if current_rule == None:
                continue
            current_list = d[each]
            cnt = 0
            Manager = eval('models.' + current_rule['model'])
            # if current_rule['is_related']:
            # for p in Manager.objects.all():
            #     p.delete()
            for each_elem in current_list:
                q = {}
                if current_rule['is_related']:
                    for each in current_rule['fields']:
                        if Manager._meta.get_field(each['django']).unique:
                            q[each['django']] = each_elem[each['c1']]
                    if len(q):
                        try:
                            finding_object = Manager.objects.get(**q)
                        except Manager.DoesNotExist:
                            finding_object = Manager()
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
                        except Manager.DoesNotExist:
                            finding_object = Manager()
                            finding_object.exchange = True
                        except MultipleObjectsReturned:
                            print(q, 'MultipleObjectsReturned: ' + str(cnt + 1) + current_rule['model'])
                            continue
                else:
                    try:
                        finding_object = Manager.objects.get(uid=each_elem[u'uid'])
                    except:
                        finding_object = Manager()
                        # if not current_rule['is_related']:
                        finding_object.uid = each_elem[u'uid']
                #
                for rule_field in current_rule['fields']:
                    value = each_elem[rule_field['c1']]
                    if value == '00000000-0000-0000-0000-000000000000':
                        value = None
                    finding_field = getattr(finding_object, rule_field['django'])
                    if type(finding_field) == bool and value == None:
                        value = False
                    if type(finding_field) == str and value == None:
                        value = ''
                    if (type(finding_field) == int or type(finding_field) == long or type(
                            finding_field) == float) and value == None:
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
            print (str(cnt) + ' ' + current_rule['model'])

        if has_not_saved:
            return HttpResponse('not_saved')
        else:
            cache.set('main_tree', None)
            models.GoodGroup.objects.rebuild()
            return HttpResponse('ok')


def complete1corders(request):
    if not request.user.is_superuser:
        return JsonResponse({'status': 1})
    orders = models.Order.objects.filter(pk=request.GET['order'])
    for each in orders:
        each.sended = True
        if each.status != 4:
            each.status = int(request.GET['status'])
        each.save()
    return JsonResponse({'status': 0})


def get1corders(request):
    if not request.user.is_superuser:
        return JsonResponse({'status': 1})
    orders = models.Order.objects.filter(sended=False)
    l = []
    tz = pytz.timezone(TIME_ZONE)
    for item in orders:
        if datetime.now(tz) - item.added.astimezone(tz) > timedelta(hours=1):
            goods = []
            for each in item.ordergood_set.filter(deleted=False):
                goods.append({
                    'good': str(each.good_id),
                    'kount': each.kount,
                    'price': each.price,
                    'charac': str(each.charac_id)
                })
            l.append(
                {
                    'uid': str(item.pk),
                    'status': item.status,
                    'pay_type': str(item.pay_type),
                    'paid': str(item.paid),
                    'kontragent': str(item.kontragent_id),
                    'kontragent_name': item.kontragent.name,
                    'kontragent_bin': item.kontragent.iinbin,
                    'kontragent_phone': item.kontragent.phone,
                    'price_type': str(item.price_type_id),
                    'date': item.added.astimezone(tz),
                    'number': item.document_number,
                    'comment': item.comment,
                    'goods': goods
                })
            if item.address_id == None:
                l[-1]['address'] = None
            else:
                l[-1]['address'] = unicode(item.address.address)
    return JsonResponse({'list': l})


def get1cpreorders(request):
    if not request.user.is_superuser:
        return JsonResponse({'status': 1})
    preorders = models.Preorder.objects.filter(sended=False)
    l = []
    tz = pytz.timezone(TIME_ZONE)
    for item in preorders:
        goods = []
        for each in item.preordergood_set.filter(deleted=False):
            goods.append({
                'good': str(each.good_id),
                'kount': each.kount,
                'price': each.price,
                'charac': str(each.charac_id)
            })
        l.append(
            {
                'uid': str(item.pk),
                'status': item.status,
                'kontragent': str(item.kontragent_id),
                'kontragent_name': item.kontragent.name,
                'kontragent_bin': item.kontragent.iinbin,
                'kontragent_phone': item.kontragent.phone,
                'price_type': str(item.price_type_id),
                'date': item.added.astimezone(tz),
                'number': item.document_number,
                'goods': goods
            })
    return JsonResponse({'list': l})


def get_delivery_addresses(request):
    if not request.user.is_superuser:
        return HttpResponse(status=403)
    sended = []
    kontragents = models.Kontragent.objects.filter(deleted=False)
    for kontragent in kontragents:
        da = []
        for each in kontragent.deliveryaddress_set.filter(deleted=False):
            da.append({
                'uid': each.uid,
                'address': each.address,
                'added': str(each.added)
            })
        sended.append({
            'k_uid': kontragent.uid,
            'name': kontragent.name,
            'addresses': da,
        })
    return JsonResponse({'list': sended})


def clear_cache(request):
    if request.user.is_superuser:
        cache.clear()
        try:
            shutil.rmtree(CACHES['default']['LOCATION'])
        except:
            pass
        return HttpResponse('ok')
    else:
        return HttpResponse(status=403)
