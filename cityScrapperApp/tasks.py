import requests
from celery import shared_task

from cityScrapperApp.CraigslistScrapper import CraigslistScrapper
from cityScrapperApp.FlipKey import FlipKeyScrapper

__author__ = 'eMaM'


@shared_task(max_retries=10)
def startScraptask(city):
    flipKey = FlipKeyScrapper()
    print 'start processing with city ' + str(city['name'])
    # start scrap
    flipKey.start_processing(city['name'])


@shared_task()
def calc(inx):
    return inx


@shared_task(max_retries=10)
def startScrapCriaglist(state, city, url):
    # http://40.65.121.61/cldownloader/processURL.php%3Fcountryname%3Dcanada%26statename%3DAlberta%26cityname%3Dcalgary%26url%3Dhttps%253A%252F%252Fcalgary.craigslist.ca%252F
    url = 'http://40.65.121.61/cldownloader/processURL.php?statename={}&cityname={}&url={}'.format(state, city, url)
    print url
    response = requests.get(url)
    if response.status_code == 200:
        return response.text


@shared_task(max_retries=10)
def CriagslistScrap(base_url, category_url, city, region):
    scrap = CraigslistScrapper(base_url=base_url, category_url=category_url, city=city, region=region,
                               country='United States')
    print 'start processing with URL ' + base_url + '|' + category_url
    # start scrap
    scrap.scrap_cl()
    return 'Complete scrap city {}'.format(city)
