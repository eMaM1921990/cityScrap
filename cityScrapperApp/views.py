# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from cityScrapperApp.SalesForce import SalesForceClass

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import csv
import sys

from cities_light.models import City
from django.shortcuts import render, redirect
from django.conf import settings
from django.db.models import Count
from django.http.response import HttpResponse
import json

# Create your views here.
from django.views.decorators.http import require_http_methods

from cityScrapperApp.FlipKey import FlipKeyScrapper
from cityScrapperApp.models import ScrapModel, ScrapDetails
from tasks import *

reload(sys)
sys.setdefaultencoding('utf8')


def index(request):
    context = {}
    template = 'index.html'
    # Get Cities
    context['cities'] = City.objects.values('name').distinct()
    context['count'] = ScrapDetails.objects.filter(phone__isnull=False).values('phone').distinct().count()
    return render(request=request,
                  template_name=template,
                  context=context)


def travelMobData(request):
    context = {}
    template = 'travelMobData.html'
    context['data'] = ScrapModel.objects.all()
    return render(request, template, context=context)


def exportPropertyUnitCount(request):
    # get data
    data = ScrapDetails.objects.filter(name__isnull=False).values('name', 'scrap__name', 'phone').annotate(
        total=Count('id')).order_by('-total')
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="property.csv"'
    writer = csv.writer(response)
    field_names = ["Manager name ", 'Location', 'count']
    writer.writerow(field_names)
    for row in data:
        if len(row['name'].encode('utf-8').strip()) > 0:
            writer.writerow(
                [row['name'].encode('utf-8').strip(), row['scrap__name'].encode('utf-8').strip(), row['phone'],
                 row['total']])
    return response


@require_http_methods(["GET"])
def exportData(request, id, name):
    # get data
    data = ScrapDetails.objects.filter(scrap__id=id)
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + name + '.csv"'
    writer = csv.writer(response)
    field_names = ["name", "first_name", "last_name", "phone_number", 'url']
    writer.writerow(field_names)
    for row in data:
        writer.writerow([row.name, row.f_name, row.l_name, row.phone, row.url])

    return response


@require_http_methods(["GET"])
def exportExtraData(request, id, name, unique):
    # get data
    if unique:
        data = ScrapDetails.objects.filter(scrap__id=id, phone__isnull=False)
    else:
        data = ScrapDetails.objects.filter(scrap__id=id, phone__isnull=False)
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + name + '.csv"'
    writer = csv.writer(response)
    field_names = ["name", "first_name", "last_name", "phone_number", 'url']
    writer.writerow(field_names)
    for row in data:
        writer.writerow([row.name, row.f_name, row.l_name, row.phone, row.url])

    return response


@require_http_methods(["POST"])
def scrap(request):
    valid = False
    cityId = request.POST.get('city')
    website = request.POST.get('website')
    if website not in settings.WEBSITE_LIST:
        ret = {
            'valid': valid,
            'msg': 'Invalid website'
        }

        return HttpResponse(json.dumps(ret, ensure_ascii=False))
    else:

        cities = City.objects.values('name').filter(name__startswith='Z').distinct()
        print cities
        job_numbers = 0
        for city in cities:
            startScraptask.delay(city)
            job_numbers += 1
            # calc.delay(10)

    return redirect(reverse(index))


def cloneSalesForceLeads(request):
    SalesForceInstance = SalesForceClass()
    # sales_force_leads_list  = SalesForceInstance.query_all_leads()
    # SalesForce.objects.bulk_create(sales_force_leads_list)

    # sales_force_leads_list = SalesForce.objects.all()
    # sales_force_leads_list = ['+'+str(o.remove_number_format) for o in sales_force_leads_list]
    #
    data = ScrapDetails.objects.filter(phone__isnull=False).values('phone').distinct()

    file = False
    if file:
        dataReader = csv.reader(open('/Users/mac/Downloads/109822.csv'), delimiter=str(u',').encode('utf-8'),
                                quotechar=str(u'"').encode('utf-8'))
        for record in dataReader:
            print '{} start phone '.format(record[2])
            # phone = str(record['phone']).replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            if record[28]:
                try:
                    # phone_records = ScrapDetails.objects.filter(phone=phone)
                    SalesForceInstance.check_and_create_lead(last_name=record[0],
                                                             phone=record[28],
                                                             campaign_source=(str(record[3]))[:25],
                                                             lead_source='AhmedCaldwellLists ',
                                                             website='',
                                                             company='HomeAway',
                                                             tags='HomeAway, scrape, house',
                                                             email='',
                                                             is_international=True)
                except Exception as e:
                    print str(e)
    else:
        for r in data:
            record = ScrapDetails.objects.filter(phone=r['phone'])
            record = record[0]
            time.sleep(10)
            SalesForceInstance.check_and_create_lead(last_name=record.name,
                                                     phone=record.phone,
                                                     campaign_source=(record.scrap.name)[:25],
                                                     lead_source='AhmedFlipKey ',
                                                     website='',
                                                     company='FlipKey',
                                                     tags='FlipKey, scrape, house',
                                                     email='',
                                                     is_international=True)

    return redirect(reverse('index'))


@require_http_methods(["POST"])
@csrf_exempt
def CriagListScrap(request):
    resp = {}
    resp['code'] = 505
    data= json.loads(request.body)
    if 'city_name' not in data or len(data['city_name']) == 0:
        resp['msg'] = 'City name is required.'
        return HttpResponse(json.dumps(resp,ensure_ascii=False))

    if 'name' not in data or len(data['name']) == 0:
        resp['msg'] = 'name is required.'
        return HttpResponse(json.dumps(resp,ensure_ascii=False))

    if 'email' not in data or len(data['email']) == 0:
        resp['msg'] = 'email is required.'
        return HttpResponse(json.dumps(resp,ensure_ascii=False))

    if 'phone' not in data or len(data['phone']) == 0:
        resp['msg'] = 'phone is required.'
        return HttpResponse(json.dumps(resp,ensure_ascii=False))

    if 'url' not in data or len(data['url']) == 0:
        resp['msg'] = 'url is required.'
        return HttpResponse(json.dumps(resp,ensure_ascii=False))
    try:
        try:
            object = ScrapModel.objects.get(name=data['city_name'], source='Craiglist')
        except ObjectDoesNotExist as e:
            object = ScrapModel()
            object.name = data['city_name']
            object.source = 'Craiglist'
            object.save()

        # create scrap details
        scrap_object = ScrapDetails()
        scrap_object.name = data['name']
        scrap_object.scrap = object
        scrap_object.f_name = data['f_name'] if 'f_name' in data else ''
        scrap_object.l_name = data['l_name'] if 'l_name' in data else ''
        scrap_object.phone = data['phone']
        scrap_object.url = data['url']
        scrap_object.save()
        resp['code'] = 200
        resp['msg'] = 'Success'
        return HttpResponse(json.dumps(resp,ensure_ascii=False))

    except Exception as e:
        resp['msg'] = str(e)
        return HttpResponse(json.dumps(resp,ensure_ascii=False))
