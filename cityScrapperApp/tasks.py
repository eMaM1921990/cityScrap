from celery import shared_task

from cityScrapperApp.FlipKey import FlipKeyScrapper

__author__ = 'eMaM'


@shared_task(max_retries=10)
def startScraptask(city):
    flipKey = FlipKeyScrapper()
    print 'start processing with city ' + str(city['name'])
    # start scrap
    flipKey.start_processing(city['name'])
