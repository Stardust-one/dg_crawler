from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


# author:武洪艳
class KongthapgovlaSpider(BaseSpider):
    name = 'kongthapgovla'
    website_id = 1629
    language_id = 2005
    # allowed_domains = ['www.kongthap.gov.la/']
    start_urls = ['https://www.kongthap.gov.la/']  # https://www.kongthap.gov.la/
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu_news > ul > li > a')
        for category in categories:
            category_url = 'https://www.kongthap.gov.la/' + category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('#listNewsSM > a')
        for article in articles:
            article_url = 'https://www.kongthap.gov.la/' + article.get('href')
            yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        next_page = 'https://www.kongthap.gov.la/' + soup.select('#listNewsSM > center:nth-child(13) > b > nav > ul > li a')[-2].get('href')
        yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('#headpageLG > div.col-xs-9 > p:nth-child(1) > font:nth-child(1) > b').text.strip()
        tt = soup.select_one('#headpageSM > font:nth-child(3)').text.split('|')[0].split(' ')
        item['pub_time'] = tt[1] + ' ' + tt[2]
        item['images'] = [img.get('src') for img in soup.select('#headpageSM > a > img')]
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('#headpageSM > div > font') if paragraph.text != '' and paragraph.text!=' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
