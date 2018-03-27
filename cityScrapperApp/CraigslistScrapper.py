import StringIO
import csv
import datetime
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMessage

from cityScrapperApp.models import ScrapModel, ScrapDetails

__author__ = 'eMaM'

from time import sleep, time
import requests


class CraigslistScrapper():
    def __init__(self, base_url, category_url, city, region, country):
        self.KEY = '722255fb8fed3c74efd8a3f36063f6ea'
        self.ITEM_PER_PAGE = 120
        self.HEADERS = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.TIME_OUT = None
        self.TIME_WAIT = 5
        self.KEY = '722255fb8fed3c74efd8a3f36063f6ea'
        self.BASE_URL = base_url
        self.CATEGORY_URL = category_url
        self.CITY = city
        self.REGION = region
        self.COUNTRY = country
        self.EXCUTE_DATE = datetime.datetime.today().date()

    # Open Http connection
    def __open_http_connection(self, call_url, page, headers=None, is_get=True):
        try:
            # print('Begin: Call URL -- {} '.format(call_url))
            sleep(self.TIME_WAIT)
            if is_get:
                scraped_html_page = requests.get(call_url, timeout=self.TIME_OUT,
                                                 params=dict(s=page), headers=self.HEADERS)
            else:
                scraped_html_page = requests.post(call_url, timeout=self.TIME_OUT, headers=self.HEADERS)
            # print('Finish: Call URL -- {} '.format(call_url))
            # Check response code
            if scraped_html_page.status_code == 200:
                return scraped_html_page.text
        except Exception as e:
            print('Error during call URL  {} cause {}'.format(call_url, str(e)))
            return None

    # parse page in soup
    def __parsePageSoap(self, page):
        soup = BeautifulSoup(page, "html.parser")
        return soup

    # Get total pages
    def __get_total_pages(self, soap_page):
        total_count_tag = soap_page.find('span', attrs={'class': 'totalcount'})
        if total_count_tag:
            return round(float(total_count_tag.text) / self.ITEM_PER_PAGE)
        return 1

    def __get_result_page_item(self, soap_page):
        sortable_results_tag = soap_page.find('div', attrs={'id': 'sortable-results'})
        if sortable_results_tag:
            li_tags = sortable_results_tag.find_all('li', attrs={'class': 'result-row'})
            for li_tag in li_tags:
                href_tag = li_tag.find('a')
                link = href_tag['href']
                # start parse target data
                self.__parse_target_page(url=link)

    def __parse_target_page(self, url):
        page_result_txt = self.__open_http_connection(call_url=url, page=None)
        if page_result_txt:
            soap_page = self.__parsePageSoap(page=page_result_txt)
            href_tag = soap_page.find('a', attrs={'id': 'replylink'})
            self.__get_site_key(url=self.BASE_URL + href_tag['href'])

    def __get_site_key(self, url):
        page_result_txt = self.__open_http_connection(call_url=url, page=None, is_get=False)
        if page_result_txt:
            soap_page = self.__parsePageSoap(page=page_result_txt)
            if soap_page:
                input_tag = soap_page.find('input', attrs={'name': 'site_key'})

                site_key = input_tag['value']
                # captcha resolver
                resolver_captcha_txt = self.__get_craiglisy_resolver(site_key=site_key, page=url)
                if resolver_captcha_txt:
                    resolver_captcha_page_soap = self.__parsePageSoap(page=resolver_captcha_txt)
                    self.__extract_contant_info(soap_page=resolver_captcha_page_soap, url=url)

    def __extract_contant_info(self, soap_page, url):
        #
        response_data = soap_page.find('div', attrs={'class': 'returnemail'})
        li_tags = response_data.find_all('li')
        if li_tags:
            contact_name_tag = li_tags[0]
            h1_tag = contact_name_tag.find('h1')
            if h1_tag and h1_tag.text == 'contact name:':
                contact_name = contact_name_tag.find('p')
        mail_tag = soap_page.find('a', attrs={'class': 'mailapp'})
        if mail_tag:
            email = mail_tag.text
        phone_tag = soap_page.find('p', attrs={'class': 'reply-tel-link'})
        if phone_tag:
            phone = str(phone_tag['href']).split(':')[1]

        self.__save_cl_result(contactname=contact_name,phone=phone,email=email,url=url)

    def __save_cl_result(self, contactname, email, phone, url):
        try:
            scrap_info = ScrapModel.objects.get(source='Craigslist',
                                                name='{},{},{}'.format(self.COUNTRY, self.REGION, self.CITY))
        except Exception as e:
            scrap_info = ScrapModel()
            scrap_info.name = '{},{},{}'.format(self.COUNTRY, self.REGION, self.CITY)
            scrap_info.source = 'Craigslist'
            scrap_info.save()

        scrap_info.scrap_model.create(
            name=contactname if contactname else '',
            phone=phone if phone else '',
            url=url,
            email=email if email else '',
            created_dated=self.EXCUTE_DATE
        )

    def __get_craiglisy_resolver(self, site_key, page):
        start_time = time()
        # send credentials to the service to solve captcha
        # returns service's captcha_id of captcha to be solved
        url = "http://2captcha.com/in.php?key={SERVICE_KEY}&method=userrecaptcha&googlekey={googlekey}&pageurl={pageurl}".format(
            SERVICE_KEY=self.KEY, googlekey=site_key, pageurl=page)
        resp = requests.get(url)
        if resp.text[0:2] != 'OK':
            quit('Error. Captcha is not received')
        captcha_id = resp.text[3:]

        # fetch ready 'g-recaptcha-response' token for captcha_id
        fetch_url = "http://2captcha.com/res.php?key=" + self.KEY + "&action=get&id=" + captcha_id
        for i in range(1, 20):
            sleep(5)  # wait 5 sec.
            resp = requests.get(fetch_url)
            if resp.text[0:2] == 'OK':
                break

        print('Time to solve: ', time() - start_time)

        # final submitting of form (POST) with 'g-recaptcha-response' token
        submit_url = page
        # spoof user agent
        headers = {'user-agent': 'Mozilla/5.0 Chrome/52.0.2743.116 Safari/537.36'}
        # POST parameters, might be more, depending on form content
        payload = {'submit': 'submit', 'g-recaptcha-response': resp.text[3:]}
        resp = requests.post(submit_url, headers=headers, data=payload)
        if resp.status_code == 200:
            return resp.text
        return None

    def scrap_cl(self):
        url = self.BASE_URL + self.CATEGORY_URL
        page_as_txt = self.__open_http_connection(call_url=url, page=0)
        if page_as_txt:
            soap_page = self.__parsePageSoap(page=page_as_txt)
            # retrieve total pages
            total_pages = self.__get_total_pages(soap_page=soap_page)
            # parse first page
            self.__get_result_page_item(soap_page=soap_page)

            for page in range(1, total_pages):
                page_as_txt = self.__open_http_connection(call_url=url, page=page * self.ITEM_PER_PAGE)
                if page_as_txt:
                    soap_page = self.__parsePageSoap(page=page_as_txt)
                    # parse first page
                    self.__get_result_page_item(soap_page=soap_page)

            # send email after parsing
            csv_data =ScrapDetails.objects.filter(scrap__name='{},{},{}'.format(self.COUNTRY, self.REGION, self.CITY),created_dated=self.EXCUTE_DATE)
            csvfile = StringIO.StringIO()
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Name', 'Phone', 'Email', 'Website', 'Location'])
            for row in csv_data:
                csvwriter.writerow([row.name, row.phone, row.email, row.url, row.scrap.name])
            message = EmailMessage("Craigslist scrap","Your criagslist scrap file ",settings.SENDER,["emam151987@gmail.com"])
            message.attach('{},{},{} - {}.csv'.format(self.COUNTRY, self.REGION, self.CITY,self.EXCUTE_DATE), csvfile.getvalue(), 'text/csv')

