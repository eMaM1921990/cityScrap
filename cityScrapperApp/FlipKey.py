import random
import requests
import json

import time

from bs4 import BeautifulSoup
from bs4 import Tag

from cityScrapperApp.models import ScrapModel, ScrapDetails

__author__ = 'eMaM'


class FlipKeyScrapper():
    def __init__(self):
        # Flip Key main website
        self.main_url = 'https://www.flipkey.com/'

        # Flip Key get target urls JSON
        self.target_urls = 'content/srp/saut/?s={}'

        # fetch result page as Json
        self.search_result_url = 'content/srp/srp_fk/index_json/{}'

        # Setting Time out
        self.timeout = None

        # Setting Sleep time
        self.time_wait = 10

        # User Agents
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]

    # Start

    def start_processing(self, name):
        print 'Target City is -----> ' + name
        URLs = self.build_target_url(city_name=name)


        # Open connection for get target urls
        connection_result = self.open_http_connection(call_url=URLs, page=None)

        print connection_result

        # Sleep for while
        time.sleep(self.time_wait)

        if connection_result:
            for url in json.loads(connection_result):
                display_name = url['Name']
                slash_name = url['SlashName']

                # Check if sSlashName exist
                if slash_name:
                    if ScrapModel.objects.filter(name=display_name).count() == 0:
                        page_no = 0

                        url = self.build_search_url(slash_name)
                        print 'start with search url ===>' + str(url)

                        # open connection for search
                        search_conn_result = self.open_http_connection(call_url=url, page=page_no)

                        print 'Total Page' + str(json.loads(search_conn_result)['tot_pages'])

                        if search_conn_result :
                            # save to databse
                            record = ScrapModel()
                            record.name = display_name
                            record.save()

                            # parse search item for first page
                            self.parse_search_items(search_conn_result, record)

                            total_pages = json.loads(search_conn_result)['tot_pages']

                            for page in range(1, total_pages):
                                # open connection for search
                                search_conn_result = self.open_http_connection(call_url=url, page=page)

                                if search_conn_result:
                                    self.parse_search_items(search_conn_result, record)

    # Build URL to get Search URLS
    def build_target_url(self, city_name):
        return self.main_url + self.target_urls.format(city_name)

    # Build Search URL
    def build_search_url(self, url):
        return self.main_url + self.search_result_url.format(url)

    # Get User Agent
    def get_random_agent(self):
        return random.choice(self.user_agent_list)

    # Open Http connection
    def open_http_connection(self, call_url, page):
        try:
            scraped_html_page = requests.get(call_url, timeout=self.timeout,
                                             params=dict(page=page))

            # Check response code
            if scraped_html_page.status_code == 200:
                return scraped_html_page.text
        except Exception as e:
            print str(e)
            return None

    # Get Search URL
    def parse_search_url(self, url_json):
        return json.loads(url_json)

    # save to database

    # Start Parse First Page
    def parse_item_page(self, url):

        print 'start adv page '+str(url)

        owner = {}
        adv_page_result = self.open_http_connection(call_url=url, page=None)

        if adv_page_result:
            soup = BeautifulSoup(adv_page_result, "html.parser")
            number = soup.find(attrs={"class": "number"})
            oname = soup.find(attrs={"class": "owner-name"}).text

            if number:
                noTag = number.contents
                number = noTag[1].text

            else:
                number = None

            owner['owner_name'] = oname
            owner['phone_number'] = number
            owner['url'] = url

        return owner

    # Parse Search page
    def parse_search_items(self, result, masterScrap):
        result = json.loads(result)['results']
        for search_item in result:
            if search_item:
                if 'advPageUrl' in search_item:
                    adv_page_url = search_item['advPageUrl']
                    owner = self.parse_item_page(url=adv_page_url)
                    if owner:
                        # if owner['phone_number']:
                        # save to database
                        record = ScrapDetails()
                        record.name = owner['owner_name']
                        record.f_name = ''
                        record.l_name = ''
                        record.phone = owner['phone_number']
                        record.url = owner['url']
                        record.scrap = masterScrap
                        record.save()
