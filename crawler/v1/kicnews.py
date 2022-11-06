from crawler.spiders import BaseSpider
import requests
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup


# author:刘鼎谦  finished_time:
class KicnewsSpider(BaseSpider):
    name = 'kicnews'
    allowed_domains = ['kicnews.org']
    start_urls = ['http://kicnews.org/']

    website_id = 1487  # 网站的id(必填)
    language_id = 2065  # 缅甸语言
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    flag = True

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-main-menu-1 > li')[1:-3]:
            meta = {'category1':i.select_one('a').text}
            for j in i.select('li > a'):
                url = j.get('href')
                if url is None:
                    continue
                meta['category2'] = j.text
                yield Request(url=url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_pub_time = re.findall('[0-9-T:]{19}',soup.select('.td-post-date time')[-1].get('datetime'))[0].replace('T',' ')
        flag = True
        if self.time is None or Util.format_time3(last_pub_time) >= int(self.time):
            for i in soup.select('.entry-title.td-module-title > a'):
                response.meta['title'] = i.get('title')
                yield Request(url=i.get('href'), meta=response.meta, callback=self.parse_item)
        else:
            self.logger.info("时间截止")
            flag=False
        if flag:
            try:
                nextPage=soup.select_one('.current ~ a').get("href")
                yield Request(url=nextPage, callback=self.parse_page, meta=response.meta)
            except:
                self.logger.info("Next page no more.")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('.td-post-featured-image img')]
        item['pub_time'] = re.findall('[0-9-T:]{19}',soup.select('.entry-date.updated.td-module-date')[-1].get('datetime'))[0].replace('T',' ')
        item['category2'] = response.meta['category2']
        try:
            item['body'] = ''.join(i.text.strip() + '\n' for i in soup.select('.td-post-content.td-pb-padding-side > p'))
            item['abstract'] = soup.soup.select_one('.td-post-content.td-pb-padding-side > p').text
        except:
            item['body'] = None
            item['abstract'] = None
        return item
