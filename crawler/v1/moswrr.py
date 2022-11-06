from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import time
from datetime import datetime


# author : 詹婕妤
class MoswrrSpider(BaseSpider):
    name = 'moswrr'
    allowed_domains = ['www.moswrr.gov.mm']
    start_urls = ['https://www.moswrr.gov.mm/']
    website_id = 1368
    language_id = 2065
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    number = {'၀': '0',
              '၁': '1',
              '၂': '2',
              '၃': '3',
              '၄': '4',
              '၅': '5',
              '၆': '6',
              '၇': '7',
              '၈': '8',
              '၉': '9'}

    month = {'ဇန်နဝါရီလ':1,
             'ဇန်နဝါရီ':1,
             'ဖေဖော်ဝါရီလ':2,
             'ဖေဖော်ဝါရီ':2,
             'မတ်လ':3,
             'မတ်':3,
             'ပြီလ':4,
             'ဧပြီ':4,
             'မေလ':5,
             'မေ':5,
             'ဇွန်':6,
             'ဇူလိုင်လ':7,
             'ဇူလိုင်' : 7,
             'သြဂုတ်လ':8,
             'စက်တင်ဘာ':9,
             'အောက်တိုဘာ':10,
             'နိုဝင်ဘာ':11,
             'ဒီဇင်ဘာ':12 }

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        category1 = soup.select_one('#menuzord > ul > li:nth-child(3) > a').text.strip()
        for i in soup.select('#menuzord > ul > li:nth-child(3) > ul > li'):
            if i.text.strip() != 'ဗီဒီယို သတင်းများ':
                url = i.find('a').get('href')
                category2 = i.text.strip()
                yield Request(url,callback=self.parse_list,meta={'category1':category1,'category2':category2})

    def parse_list(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        if response.meta['category2'] == 'လွှတ်တော်အတွင်းဆောင်ရွက်ချက်များ':
            for i in soup.select('#pyithu > article'):
                url = i.select_one('div.event-details.p-15 > a').get('href')
                title = i.select_one('div.event-details.p-15 > h5 > a').text.strip()
                response.meta['title'] = title
                yield Request(url,callback=self.parse_news,meta=response.meta)

            if soup.select_one('#pyithu').find(class_='pagination').select('li')[-1].find('a'):
                next_url = soup.select_one('#pyithu').find(class_='pagination').select('li')[-1].find('a').get('href')
                url = soup.select('#pyithu > article')[-1].select_one('div.event-details.p-15 > a').get('href')
                response.meta['next_url'] = next_url
                yield Request(url, callback=self.parse_page, meta=response.meta, dont_filter=True)

            for a in soup.select('#national > article'):
                url = a.select_one('div.event-details.p-15 > a').get('href')
                title = a.select_one('div.event-details.p-15 > h5 > a').text.strip()
                response.meta['title'] = title
                yield Request(url, callback=self.parse_news, meta=response.meta)

            if soup.select_one('#national').find(class_='pagination').select('li')[-1].find('a'):
                next_url = soup.select_one('#national').find(class_='pagination').select('li')[-1].find('a').get('href')
                url = soup.select('#national > article')[-1].select_one('div.event-details.p-15 > a').get('href')
                response.meta['next_url'] = next_url
                yield Request(url, callback=self.parse_page, meta=response.meta, dont_filter=True)

        else:
            for i in soup.select('div.col-md-9 > div > article'):
                url = i.select_one('div.event-details.p-15 > a').get('href')
                title = i.select_one('div.event-details.p-15 > h5 > a').text.strip()
                response.meta['title'] = title
                yield Request(url, callback=self.parse_news, meta=response.meta)

            if soup.find(class_='pagination').select('li')[-1].find('a'):
                next_url = soup.find(class_='pagination').select('li')[-1].find('a').get('href')
                url = soup.select('div.col-md-9 > div > article')[-1].select_one('div.event-details.p-15 > a').get('href')
                response.meta['next_url'] = next_url
                yield Request(url,callback=self.parse_page,meta=response.meta,dont_filter=True)

    def parse_page(self,response): #判断截止
        soup = BeautifulSoup(response.text,'html.parser')
        pub_time = soup.find(class_='event-content pull-left flip').select_one('p').text.strip() if soup.find(class_='event-content pull-left flip').select_one('p') else '0000-00-00 00:00:00'

        if pub_time != '0000-00-00 00:00:00':
            day = ''
            year = ''
            for i in pub_time.split()[0]:
                day += self.number[i]
            for a in pub_time.split()[2]:
                year += self.number[a]
            pub_time = time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(year), self.month[pub_time.split()[1].strip()], int(day)).timetuple())
        # if pub_time != '0000-00-00 00:00:00':
            if self.time == None or Util.format_time3(pub_time) >= int(self.time):
                yield Request(response.meta['next_url'],callback=self.parse_list,meta=response.meta)
            else:
                self.logger.info('时间截止')

        else:
            yield Request(response.meta['next_url'],callback=self.parse_list,meta=response.meta)

    def parse_news(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        images = ['https://www.moswrr.gov.mm' + soup.find(class_='post-thumb thumb').find('img').get('src')] if soup.find(class_='post-thumb thumb') else []
        if soup.find(class_='p-15').find_all('img'):
            for img in soup.find(class_='p-15').find_all('img'):
                if (images != [] and 'https://www.moswrr.gov.mm' + img.get('src') != images[0]) or images == []:
                    images.append('https://www.moswrr.gov.mm' + img.get('src'))
        pub_time = soup.find(class_='event-content pull-left flip').select_one('p').text.strip() if soup.find(class_='event-content pull-left flip').select_one('p') else '0000-00-00 00:00:00'

        if pub_time != '0000-00-00 00:00:00':
            day = ''
            year=''
            for i in pub_time.split()[0]:
                day += self.number[i]
            for a in pub_time.split()[2]:
                year += self.number[a]
            pub_time = time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(year),self.month[pub_time.split()[1].strip()],int(day)).timetuple())
        body = ''
        if soup.select('div.p-15 > table > tbody > tr'):
            for tr in soup.select('div.p-15 > table > tbody > tr'):
                for td in tr.select('td'):
                    body += td.text.strip + '\n'
        if soup.find(class_='p-15').select('p'):
            for p in soup.find(class_='p-15').select('p'):
                body += p.text.strip() + '\n'
        if soup.select('div.p-15 > ul > li'):
            for li in soup.select('div.p-15 > ul > li'):
                body += li.text.strip() + '\n'

        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = pub_time
        item['images'] = images
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        yield item

