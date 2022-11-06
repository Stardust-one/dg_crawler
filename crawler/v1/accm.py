from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import time
from datetime import datetime

# author ： 詹婕妤

class AccmSpider(BaseSpider):
    name = 'accm'
    allowed_domains = ['www.accm.gov.mm']
    start_urls = ['https://www.accm.gov.mm/acc/']
    website_id = 1382
    language_id = 2065
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'local_crawler',
    #     'password': 'local_crawler',
    #     'db': 'local_dg_test'
    # }

    
        
        

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        for i in soup.select('#bs-megamenu > ul > li')[1:-2]:
            category1 = i.find('a').text.strip()
            self.logger.info(category1)
            if category1 == 'တားဆီးကာကွယ်ရေး':
                url = 'https://www.accm.gov.mm/acc/' + i.find('a').get('href')
                yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': None})
            else:
                if category1 == 'ကော်မရှင်အကြောင်း':
                    category2 = i.select_one('div > div > ul > li:nth-child(5) > a').text.strip()
                    url = 'https://www.accm.gov.mm/acc/' + i.select_one('div > div > ul > li:nth-child(5) > a').get('href')
                    yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': category2})
                else:
                    for li in i.select('div > div > ul > li'):
                        category2 = li.find('a').text.strip()
                        if category2 != 'တိုင်ကြားရန်':
                            url = 'https://www.accm.gov.mm/acc/' + li.find('a').get('href')
                            yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': category2})

    def parse_list(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        pub = soup.find_all(class_='article-thumb')[-1].find(class_='article-date').text.strip().split(',')[-1].strip().split()
        pub = time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(pub[-1]), Util.month[pub[1]], int(pub[0])).timetuple())
        if self.time == None or Util.format_time3(pub) >= int(self.time):
            for i in soup.find_all(class_='article-thumb'):
                url = i.select_one('div.article-title > a').get('href')
                response.meta['title'] = i.select_one('div.article-title > a').text.strip()
                pub_time = i.find(class_='article-date').text.strip().split(',')[-1].strip().split()
                response.meta['pub_time'] = time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(pub_time[-1]), Util.month[pub_time[1]], int(pub_time[0])).timetuple())
                # self.logger.info(url)
                yield Request(url, callback=self.parse_news, meta=response.meta)
        # self.logger.info(pub)
        if soup.find(class_='pagination'):
            if soup.select('ul.pagination > li')[-2].find('a').text == '>':
                next_url = soup.select('ul.pagination > li')[-2].find('a').get('href')
                self.logger.info(next_url)
                if self.time == None or Util.format_time3(pub) >= int(self.time):
                    yield Request(next_url, callback=self.parse_list, meta=response.meta)
                else:
                    self.logger.info('时间截止')

    def parse_news(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        images = [img.get('src') for img in soup.find(class_='main').find_all('img')] if soup.find(class_='main').find_all('img') else []
        body = ''
        for i in soup.find(class_='main').find_all(class_='article-details'):
            body += i.text.strip() + '\n'
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = images
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        return item