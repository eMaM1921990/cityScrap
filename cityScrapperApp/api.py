from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import never_cache
from django.views.decorators.gzip import gzip_page
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from cityScrapperApp.models import ScrapModel, ScrapDetails

__author__ = 'eMaM'


@gzip_page
@never_cache
@api_view(['POST'])
@parser_classes((JSONParser,))
def CriagListScrap(request):
    resp = {}
    resp['code'] = 505
    if 'city_name' not in request.data or len(request.data['city_name'])==0:
        resp['msg'] = 'City name is required.'
        return Response(resp)

    if 'name' not in request.data or len(request.data['name'])==0:
        resp['msg'] = 'name is required.'
        return Response(resp)

    if 'email' not in request.data or len(request.data['email'])==0:
        resp['msg'] = 'email is required.'
        return Response(resp)

    if 'phone' not in request.data or len(request.data['phone'])==0:
        resp['msg'] = 'phone is required.'
        return Response(resp)

    if 'url' not in request.data or len(request.data['url'])==0:
        resp['msg'] = 'url is required.'
        return Response(resp)
    try:
        try:
            object = ScrapModel.objects.get(name=request.data['city_name'], source='Craiglist')
        except ObjectDoesNotExist as e:
            object = ScrapModel()
            object.name = request.data['city_name']
            object.source = 'Craiglist'
            object.save()

        # create scrap details
        scrap_object = ScrapDetails()
        scrap_object.name = request.data['name']
        scrap_object.scrap = object
        scrap_object.f_name = request.data['f_name'] if 'f_name' in request.data else ''
        scrap_object.l_name = request.data['l_name'] if 'l_name' in request.data else ''
        scrap_object.phone = request.data['phone']
        scrap_object.url = request.data['url']
        scrap_object.save()
        resp['code'] = 200
        resp['msg'] = 'Success'
        return Response(resp)


    except Exception as e:
        resp['msg'] = str(e)
        return Response(resp)
