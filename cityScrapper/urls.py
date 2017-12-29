"""travelmob URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from cityScrapperApp import api
from cityScrapperApp.views import index, scrap, travelMobData, exportData, exportExtraData, exportPropertyUnitCount, \
    cloneSalesForceLeads

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index,name='index'),
    url(r'^scrap/$', scrap,name='scrap'),
    url(r'^data/$', travelMobData,name='travelMobData'),
    url(r'^export/(?P<id>.*)/(?P<name>.*)/$', exportData,name='exportData'),
    url(r'^export/(?P<id>.*)/(?P<name>.*)/(?P<unique>.*)$', exportExtraData,name='exportExtraData'),
    url(r'^propertyManager/$', exportPropertyUnitCount,name='propertyManager'),
    url(r'^sales_force/$', cloneSalesForceLeads,name='cloneSalesForceLeads'),


    url(r'^api/v1/craiglist/$', api.CriagListScrap, name='CriagListScrap'),
    url(r'^api/v1/flipkey/(?P<name>.*)/$', api.ScrappService, name='flipkeyAPI'),
]
