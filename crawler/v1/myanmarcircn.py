from crawler.spiders import BaseSpider
import json

import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup

# author 刘鼎谦
class MyanmarcircnSpider(BaseSpider):
    name = 'myanmarcircn'
    allowed_domains = ['myanmar.cri.cn']
    start_urls = [
                  'http://myanmar.cri.cn/news/domestic/list.html',
                  'http://myanmar.cri.cn/news/International/list.html',
                  'http://myanmar.cri.cn/news/asean/list.html']

    website_id =  1450 # 网站的id(必填)
    language_id =  2065 # 语言
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

    cate ={
        'domestic':'တရုတ္',
        'International':'ႏုိင္ငံတကာ',
        'asean':'တရုတ္-အာဆီယံ'
    }

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_pub =soup.select('h4')[-1].select_one('i').text + ' 00:00:00'
        flag=True
        if self.time is None or (Util.format_time3(last_pub)) >= int(self.time):
            for i in soup.select('h4'):
                meta={
                    'category2': self.cate[response.url.split('/')[4]],
                    'title':i.select_one('a').text.strip(),
                    'pub_time':i.select_one('i').text + ' 00:00:00'
                }
                yield Request(url='http://myanmar.cri.cn'+i.select_one('a').get('href'),callback=self.parse_item,meta=meta)
        else:
            self.logger.info("时间截止")
            flag = False
        if flag:
            try:
                js=json.loads(soup.select_one('.list-box.txt-listUl > ul').get('pagedata'))
                nextPage='http://myanmar.cri.cn'+js['urls'][js['current']]
                yield Request(url=nextPage)
            except:
                self.logger.info("Next page no more")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = 'သတင္း'
        item['title'] = response.meta['title']
        item['images'] = ['http'+i.get('src') for i in soup.select('#abody img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = response.meta['category2']
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('#abody p')])
        item['abstract'] = response.meta['title']
        return item