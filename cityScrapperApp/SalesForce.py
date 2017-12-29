from django.conf import settings

from simple_salesforce import Salesforce
import re

# from travelmobApp.models import SalesForce
from cityScrapperApp.models import SalesForce

__author__ = 'eMaM'

E164_RE = re.compile('^\+\d{11}$')


class SalesForceClass():
    def __init__(self):
        self.sf = Salesforce(
            username=settings.USERNAME,
            password=settings.PASS,
            security_token=settings.TOKEN,
            # sandbox=True
        )

    def get_lead_object(self, last_name, phone, campaign_source, lead_source, website, company, tags, is_international,email):
        return {
            'Status': 'New',  # static
            'LastName': last_name,  # put whole name string into last name
            'Phone': phone,  # phone number formatted to E.164 number formatting. +[countrycode][areacode][number]
            'Campaign_Source__c': campaign_source,  # City and State (and country if applicable)
            'LeadSource': lead_source,  # website name and medium. For example: HomeAway Website,
            'Website': website,  # Advertising website
            'Rating': '1. New',  # Static
            'Company': company,  # website name
            'Tag_Cloud__c': tags,  # random tags, i used source, method, property type.
            'International_Phone__c': is_international,
            'Email':email
        }

    def create_lead(self, last_name, phone, campaign_source, lead_source, website, company, tags, is_international,email):
        lead_obj = self.get_lead_object(last_name, phone, campaign_source, lead_source, website, company, tags,
                                        is_international,email)
        self.sf.Lead.create(lead_obj)

    # Pulls all phone numbers. Phone numbers are not all the same format, so numbers will need to be standardized or converted before comparison
    def query_all_leads(self):
        tables = ['Lead', 'Contact', 'Account']
        # tables = ['lead']
        entries = []
        for each in tables:
            entries += self.create_leads_models(leads_dict=self.sf.query_all("select Id, Phone from {}".format(each)))
            # entries.extend(self.sf.query_all("select Id, Phone from {}".format(each)))
        return entries

    def create_leads_models(self, leads_dict):
        leads = []
        for lead in leads_dict['records']:
            if lead['Phone']:
                leads.append(
                    SalesForce(
                        sales_force_id=lead['Id'],
                        sales_force_phone=lead['Phone'],
                    )
                )
        return leads

    # You can use this to create a single lead to salesforce
    def check_and_create_lead(self, last_name, phone, campaign_source, lead_source, website, company, tags,
                              is_international,email):
        if not self.phone_exist(phone):
            self.create_lead(
                last_name=last_name,
                phone=phone,
                campaign_source=campaign_source,
                lead_source=lead_source,
                website=website,
                company=company,
                tags=tags,
                is_international=is_international,
                email=email
            )
            print '{} new phone created'.format(phone)

    def tests(self):
        return self.sf.Contact.create({'LastName': 'Ahmed', 'Email': 'eMaM151987@gmail.com'})

    def phone_exist(self, phone):
        query = "SELECT Id, Name FROM Lead WHERE Phone = '{}'".format(phone)
        query_result = self.sf.query_all(query)
        if len(query_result['records']) > 0:
            print '{}  phone is exist'.format(phone)
            return True
        else:
            print '{}  phone not exist'.format(phone)
            return False

# check_and_create_lead(
#     last_name='(Fake do not process) Joe & Mathers Fava',
#     phone='16268645227',
#     campaign_source='Panama City, FL',
#     lead_source='Flipkey Website',
#     website='https://www.flipkey.com/properties/8801586/',
#     company='Flipkey',
#     tags='flipkey, scrape, house',
#     is_international=True
# )
