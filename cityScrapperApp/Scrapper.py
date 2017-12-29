import re

import requests
import time
from bs4 import BeautifulSoup
from django.conf import settings
import json

try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs

__author__ = 'eMaM'


class Scrapper():
    def __init__(self, scrapUrl, country, region, city):
        self.scrapUrl = scrapUrl
        self.country = country
        self.region = region
        self.city = city

    def scrap_main(self):
        baseUrl = self.scrapUrl + self.country + '/' + self.region + '/' + self.city
        print baseUrl
        scrapped_data = []
        scraped_page = self.scrape_url(URL=baseUrl)

        if scraped_page:
            # scrap pagination
            page_count = self.get_pagination(page=scraped_page)
            page_count = 5
            # start scrap
            print 'start scrap page 1'
            # scape page result card
            page_scraped = self.scrap_result_page(pageContent=scraped_page)

            scrapped_data += page_scraped

            for pageCursor in range(2, page_count):
                print 'start scrap page ' + str(pageCursor)
                scraped_page = self.scrape_url(URL=baseUrl, page=pageCursor)
                # scape page result card
                page_scraped = self.scrap_result_page(pageContent=scraped_page)
                scrapped_data += page_scraped
                # sleep for while
                time.sleep(5)
                # print len(scrapped_data)
        # print scrapped_data[0]
        return scrapped_data

    # scrap any URL
    def scrape_url(self, URL, timeout=None, headers=None, page=None):
        if not page:
            scraped_html_page = requests.get(URL, timeout=timeout, headers=headers, params=dict(page=page))
            time.sleep(10)
        else:

            scraped_html_page = requests.get(URL, timeout=timeout, headers=headers)
            time.sleep(10)

        # Check response code
        if scraped_html_page.status_code == 200:
            return scraped_html_page.text
        return None

    # Scrap get_pagination
    def get_pagination(self, page):

        paginationArray = [1]

        soup = BeautifulSoup(page, "html.parser")
        paginatorDiv = soup.find("div", id='paginator')
        ulElementTag = paginatorDiv.find("ul")
        if ulElementTag:
            for hrefElement in ulElementTag.find_all("a"):
                urlValue = hrefElement['href']
                print urlValue
                if urlValue != '#':
                    pageCount = self.get_result_counts(urlValue)
                    if pageCount:
                        paginationArray.append(int(pageCount[0]))

        paginationArray.sort(reverse=True)
        return paginationArray[0]

    # Extract Attribute value from URL
    def get_result_counts(self, url):
        o = urlparse(url)
        query = parse_qs(o.query)
        if 'page' in query:
            return query['page']
        return None

    # Scrap current page
    def scrap_result_page(self, pageContent):
        page_detail = []
        soup = BeautifulSoup(pageContent, "html.parser")
        tag = soup.find("div", id="spaces").find_all("a", "space tclick")
        for link in tag:
            hrefAttr = link['href']
            if link["data-tloc"] == 'Native':
                # Get Target URL
                targetUrl = self.getTravelMobURL(hrefAttr)

                # Scrap Target URL
                page = self.scrape_url(URL=targetUrl)

                # Scrap detail page
                object = self.scrapTravelMobPage(page, targetUrl)
                if object:
                    # print object
                    page_detail.append(object)

            else:
                # Get Target URL
                targetUrl = self.buildHomawayURL(hrefAttr)
                targetUrl = 'https://www.travelmob.com'+hrefAttr
                # Scrap Target URL
                time.sleep(10)
                page = self.scrape_url(URL=targetUrl)
                time.sleep(10)
                # Scrap detail page
                object = self.scrapHomeAway(page, targetUrl)
                if object:
                    # print object
                    page_detail.append(object)

        return page_detail

    # Get Paramer
    def getParamter(self, url):
        return url.split('?')[0]

    # Scrap Target
    def getTravelMobURL(self, url):
        targetUrl = 'https://www.travelmob.com'
        targetUrl += self.getParamter(url)
        return targetUrl

    # Scrap details Page
    def scrapTravelMobPage(self, page, url):
        soup = BeautifulSoup(page, "html.parser")
        body = soup.find('body')
        text = body.select('script')[1].text
        text = text.replace("dataLayer.push(", "")
        text = text.replace(");", "")
        result = json.loads(text.encode(encoding='UTF-8', errors='strict'))
        name = result['user']['name'] if hasattr(result['user'], 'name') else None
        first_name = result['user']['first_name'] if 'first_name' in result['user'] else None
        last_name = result['user']['last_name'] if 'last_name' in result['user'] else None
        phone_number = result['user']['phone_number'] if 'phone_number' in result['user'] else None

        dict = self.buildDictObject(name, first_name, last_name, phone_number, url)
        return dict

    # build dictionary
    def buildDictObject(self, name, first_name, last_name, phone_number, url):
        dict = {}
        dict['name'] = name
        dict['first_name'] = first_name
        dict['last_name'] = last_name
        dict['phone_number'] = phone_number
        dict['url'] = url
        return dict

    def buildHomawayURL(self, url):
        targetUrl = 'http://asia.homeaway.com/vacation-rental/'
        targetUrl += self.getParamter(url)
        return targetUrl

    def scrapHomeAway(self, page, url):
        print url
        soup = BeautifulSoup(page, "html.parser")
        body = soup.find('body')
        phone_number = None
        owner_name = None
        first_name= None
        last_name = None
        for tag in body.findAll('span'):
            if tag.has_attr('class'):
                if tag['class'][0] == 'booking-phone':
                    phone_number = tag.contents[0]

                if tag['class'][0] == 'owner-name':
                    owner_name = tag.contents[0]

        if not owner_name:
            owner_name = 'owner'
            first_name = owner_name
            last_name = owner_name

        if len(owner_name.split()) > 1:
            first_name = owner_name.split()[0]
            last_name = owner_name.split()[1]
        else:
            first_name = owner_name
            last_name = ''

        url = url.split('?')[0]

        dict = self.buildDictObject(owner_name,
                                    first_name,
                                    last_name,
                                    phone_number,
                                    url)

        return dict
