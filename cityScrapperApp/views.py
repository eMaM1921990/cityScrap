# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
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

        cities = City.objects.values('name').filter(name__startswith='S').distinct()
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
    # data = ScrapDetails.objects.filter(phone__isnull=False).values('phone').distinct()
    # dataList = [str(o['phone']).replace("(", "").replace(")", "").replace("-", "").replace(" ", "") for o in data]
    # for sales_force_number in sales_force_leads_list:
    #     data = data.exclude(phone=sales_force_number)
    # data = data.values('phone').distinct()
    # listOne = ['a','b','c']
    # listTwo = ['d']
    # data = list(set(listOne)-set(listTwo))

    # data = list(set(dataList)-set(sales_force_leads_list))


    dataReader = csv.reader(open('/Users/mac/Downloads/Vacation Rentals Cleaning contacts.csv'), delimiter=str(u',').encode('utf-8'),
                            quotechar=str(u'"').encode('utf-8'))
    for record in dataReader:
        print '{} start phone '.format(record[2])
        # phone = str(record['phone']).replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        if record[3]:
            try:
                # phone_records = ScrapDetails.objects.filter(phone=phone)
                SalesForceInstance.check_and_create_lead(last_name=record[0],
                                                         phone=record[3],
                                                         campaign_source=(str(record[2]).split(',')[0])[:25],
                                                         lead_source='AhmedHomeAway ',
                                                         website='',
                                                         company='HomeAway',
                                                         tags='HomeAway, scrape, house',
                                                         email=record[4] if record[4] else '',
                                                         is_international=True)
            except Exception as e:
                print str(e)

    return redirect(reverse('index'))
