import requests
from bs4 import BeautifulSoup

from cityScrapperApp.models import CriagslistCities

__author__ = 'eMaM'


# Open Http connection
def open_http_connection(call_url, page, headers=None, is_get=True):
    try:
        scraped_html_page = requests.get(call_url, timeout=None,
                                         params=dict(s=page))
        # Check response code
        if scraped_html_page.status_code == 200:
            return scraped_html_page.text
    except Exception as e:
        print('Error during call URL  {} cause {}'.format(call_url, str(e)))
        return None


# parse page in soup
def parsePageSoap(page):
    soup = BeautifulSoup(page, "html.parser")
    return soup


def parseCities():
    html_page_txt = open_http_connection(call_url='https://www.craigslist.org/about/sites', page=None)
    if html_page_txt:
        soap_page = parsePageSoap(html_page_txt)
        colmask_tags = soap_page.find_all('div', attrs={'class': 'colmask'})
        if colmask_tags:
            colmask_tag = colmask_tags[0].contents
            region = None
            for tag in colmask_tag:
                if tag.name == 'div':
                    cities_region = tag.contents
                    for inf in cities_region:
                        if inf.name == 'h4':
                            region = inf.text
                        if inf.name == 'ul':
                            li_tags = inf.find_all('li')
                            for li in li_tags:
                                a_tag = li.find('a')
                                link = a_tag['href']
                                city = a_tag.text
                                record = CriagslistCities(region=str(region), city=str(city), url=str(link))
                                record.save()


