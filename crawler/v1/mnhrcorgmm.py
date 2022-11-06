from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from datetime import datetime

# author ： 詹婕妤
# 没有翻页

class MnhrcorgmmSpider(BaseSpider):
    name = 'mnhrcorgmm'
    allowed_domains = ['www.mnhrc.org.mm']
    start_urls = ['http://www.mnhrc.org.mm/']
    website_id = 1383
    language_id = 2065

    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'local_crawler',
    #     'password': 'local_crawler',
    #     'db': 'local_dg_test'
    # }
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        if soup.select_one('#menu-item-1527'):
            category1 = soup.select_one('#menu-item-1527 > a').text.strip()
            url = 'http://www.mnhrc.org.mm' + soup.select_one('#menu-item-5121 > a').get('href')
            category2 = soup.select_one('#menu-item-5121 > a').text.strip()
            yield Request(url,callback=self.parse_list,meta={'category1':category1,'category2':category2})
        if soup.select_one('#menu-item-1529'):
            category1 = soup.select_one('#menu-item-1529 > a').text.strip()
            url = 'http://www.mnhrc.org.mm' + soup.select_one('#menu-item-1529 > a').get('href')
            yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': None})
            if soup.select_one('#menu-item-5561'):
                category2 = soup.select_one('#menu-item-5561 > a').text.strip()
                url = 'http://www.mnhrc.org.mm' + soup.select_one('#menu-item-5561 > a').get('href')
                yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': category2})

    def parse_list(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        for i in soup.find(class_='entry-content').find_all('a'):
            url = i.get('href') if i.get('href').split('/')[0] == 'http:' else 'http://www' + i.get('href')
            response.meta['title'] = i.text.strip()
            yield Request(url,callback=self.parse_news,meta=response.meta)

    def parse_news(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        if soup.find('article'):
            body = ''
            if soup.find(class_='entry-meta'):
                body += soup.find(class_='entry-meta').text.strip() + '\n'
            if soup.find(class_='entry-content'):
                for p in soup.select('div.entry-content > p'):
                    body += p.text.strip() + '\n'
            images = [img.get('src') for img in soup.find('article').find_all('img')] if soup.find('article').find_all('img') else []
            item['category1'] = response.meta['category1']
            item['category2'] = response.meta['category2']
            item['title'] = response.meta['title']
            item['images'] = images
            item['body'] = body
            item['abstract'] = body.split('\n')[0]
            item['pub_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            yield item