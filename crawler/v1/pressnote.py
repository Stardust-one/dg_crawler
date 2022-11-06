from crawler.spiders import BaseSpider

import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time


class PresSpider(BaseSpider):
    name = 'pressnote'
    allowed_domains = ['pressnote.in']
    start_urls = ['http://pressnote.in/']
    website_id = 1045  # 网站的id(必填)
    language_id = 1930  # 所用语言的id

    def parse(self, response):
        soup = BeautifulSoup(response.text)
        for i in soup.select('#mainmenu a')[1:]:
            if re.findall("https",i.get('href')):
                meta = {'category1': i.text}
                yield Request(url=i.get('href'), meta=meta, callback=self.parse_essay)

    def parse_essay(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        for i in soup.find_all(class_='fbt-col-lg-12 col-md-4 col-xs-6 padding-reset'):
            tt = soup.select_one('.post-info').text.split()
            pub_time = Util.format_time2(tt[1]+' '+tt[0]+' '+tt[2])
            response.meta['title'] = soup.select_one('.post-content h3').text.strip()
            response.meta['pub_time'] = pub_time
            if self.time is None or Util.format_time3(pub_time) >= int(self.time):
                yield Request(url=i.select_one('.post-content a').get('href'), meta=response.meta, callback=self.parse_item)
            else:
                flag = False
                self.logger.info('时间截止')
                break
        if flag:
            try:
                if soup.find_all(class_='NavigationButton')[-1].get('value') == 'Next':
                    nextPage = soup.find_all(class_='NavigationButton')[-1].get('onclick').replace("window.location='", '')[:-2]
                    if re.match('http',nextPage):
                        yield Request(nextPage, meta=response.meta, callback=self.parse_essay)
                    else:
                        nextPage ='https://www.pressnote.in/'+ nextPage
                        yield Request(nextPage, meta=response.meta, callback=self.parse_essay)
            except:
                self.logger.info('Next page no more')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        if re.findall('English_News',response.url):
            item['language_id'] = 1866
            print('1'*1000)
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        ss = ''
        for i in soup.select('#DivContents p'):
            ss += i.text.strip() + '\n'
        item['body'] = ss
        item['abstract'] = ss.split('\n')[0]
        item['images'] = [i.get('src') for i in soup.select('#DivContents img')]
        item['category2'] = None
        item['pub_time'] = response.meta['pub_time']
        yield item