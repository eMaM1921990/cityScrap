# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_200_OK

from cityScrapperApp.CLCities import parseCities
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
from cityScrapperApp.models import ScrapModel, ScrapDetails, CriagslistCities
from tasks import *

reload(sys)
sys.setdefaultencoding('utf8')


def index(request, **kwargs):
    context = {}
    template = 'index.html'
    # Get Cities
    context['cities'] = City.objects.values('name').distinct()
    context['criaglist_cities'] = CriagslistCities.objects.all().order_by('region')
    context['count'] = ScrapDetails.objects.filter(phone__isnull=False).values('phone').distinct().count()

    if kwargs.get('msg'):
        context['msg'] = kwargs.get('msg')
    return render(request=request, template_name=template, context=context)


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
        startScraptask.delay(cityId)

    return redirect(reverse(index))


@require_http_methods(["POST"])
def scrap_criaglist(request):
    cityId = request.POST.get('city')
    category = request.POST.get('category')
    print cityId
    CriagslistScrap.delay(cityId.split(',')[1],category, cityId.split(',')[2], cityId.split(',')[0])
    return redirect(reverse(index), msg='Request send and ready for scrapping')


def cloneSalesForceLeads(request):
    SalesForceInstance = SalesForceClass()
    #
    data = ScrapDetails.objects.filter(phone__isnull=False).values('phone').distinct()
    # data = None
    file = False
    if file:
        dataReader = csv.reader(open('/Users/mac/Downloads/data/tripz_data_unique.csv'), delimiter=str(u',').encode('utf-8'),
                                quotechar=str(u'"').encode('utf-8'))
        for record in dataReader:
            print '{} start phone '.format(record[1])
            # phone = str(record['phone']).replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            if record[2]:
                try:
                    # phone_records = ScrapDetails.objects.filter(phone=phone)
                    SalesForceInstance.check_and_create_lead(last_name=record[3],
                                                             phone=record[2],
                                                             campaign_source='Tripz',
                                                             lead_source='Ahmed_Tripz',
                                                             website=record[1],
                                                             company='--',
                                                             tags='--',
                                                             is_international=False,
                                                             city=str(record[0]).split("|")[0],
                                                             notes=record[4])

                    # SalesForceInstance.update(id=record[0],city=record[2],phone=record[38])
                except Exception as e:
                    print str(e)
    else:
        for r in data:
            record = ScrapDetails.objects.filter(phone=r['phone'])
            record = record[0]
            time.sleep(5)
            print record.scrap.name
            SalesForceInstance.check_and_create_lead(last_name=record.name,
                                                     phone=record.phone,
                                                     campaign_source=((record.scrap.name).split(','))[0],
                                                     lead_source='AhmedFlipKey' if record.scrap.source == 'FlipKey' else 'AhmedCraigslist',
                                                     website=record.url,
                                                     company='Flipkey' if record.scrap.source == 'FlipKey' else 'Craigslist',
                                                     tags='Flipkey, scrape, house' if record.scrap.source == 'FlipKey' else 'Craigslist, scrape, house',
                                                     email=record.email if record.email else '',
                                                     is_international=True)

    return redirect(reverse('index'))


@require_http_methods(["GET"])
@csrf_exempt
def CriagListScrap(request):
    send_mail(message='test',subject='send grid',fail_silently=True,from_email=settings.SENDER,recipient_list=['emam151987@gmail.com'])
    return HTTP_200_OK

