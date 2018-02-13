from django.db.models.signals import post_save
from django.dispatch import receiver

from cityScrapperApp.SalesForce import SalesForceClass
from cityScrapperApp.models import ScrapDetails

__author__ = 'eMaM'

#@receiver(post_save, sender=ScrapDetails)
def ScrapDetailsSingal(sender, instance, **kwargs):
    SalesForceInstance = SalesForceClass()
    if instance.phone:
        SalesForceInstance.check_and_create_lead(last_name=instance.name,
                                                 phone=instance.phone,
                                                 campaign_source=(str(instance.scrap.name).split(',')[0])[:25],
                                                 lead_source='AhmedFlipKey' if instance.scrap.source == 'FlipKey' else 'AhmedCL',
                                                 website=instance.url,
                                                 company='FlipKey' if instance.scrap.source == 'FlipKey' else 'Criaglist',
                                                 tags='HomeAway, scrape, house',
                                                 email='',
                                                 is_international=True)
