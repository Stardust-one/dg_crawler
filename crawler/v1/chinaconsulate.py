from crawler.spiders import BaseSpider
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup

# author 刘鼎谦
class ChinaconsulateSpider(BaseSpider):  # 本网站不用翻页
    name = 'chinaconsulate'
    #allowed_domains = ['http://mandalay.china-consulate.org/chn/xwdt/']
    start_urls = ['http://mandalay.china-consulate.org/chn/xwdt/']

    website_id = 1453  # 网站的id(必填)
    language_id =  1813 # 语言
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
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.select('div>table')
        meta={}
        for i in tables:
            time=i.select_one('font').text[1:-1] + ' 00:00:00'
            if self.time is None or Util.format_time3(time) >= int(self.time):
                meta['title'] = i.select_one('a').text
                meta['pub_time'] = time
                url = i.select_one('a').get('href').replace(r'./', 'http://mandalay.china-consulate.org/chn/xwdt/')
                yield Request(callback=self.parse_item, meta=meta,url=url)
            else:
                self.logger.info("时间截止")
                break

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = '新闻动态'
        item['title'] = response.meta['title']
        item['images'] = [i.get('src').replace('./','http://mandalay.china-consulate.org/chn/xwdt/') for i in soup.select('#article img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('#article p')])
        item['abstract'] = item['title']
        return item