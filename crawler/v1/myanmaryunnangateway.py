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
class MyanmaryunnangatewaySpider(BaseSpider):
    name = 'myanmaryunnangateway'
    #allowed_domains = ['http://myanmar.yunnangateway.com/html/xinwen/']
    start_urls = ['http://myanmar.yunnangateway.com/html/xinwen/',
                  'http://myanmar.yunnangateway.com/html/wenjiao/']

    website_id = 1460  # 网站的id(必填)
    language_id = 2065  # 语言
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
        last_pub = soup.select_one('.dates.fr').text.strip()
        flag=True
        if self.time is None or (Util.format_time3(last_pub)) >= int(self.time):
            for i in soup.select('.container.w100.fl'):
                url=i.select_one('a').get('href')
                meta={
                    'title':i.select_one('a').text,
                    'pub_time':i.select_one('.dates.fr').text.strip()
                }
                yield Request(url=url, callback=self.parse_item,meta=meta)
        else:
            self.logger.info("时间截止")
            flag = False
        if flag:
            try:
                nextPage='http://myanmar.yunnangateway.com'+soup.select_one('#pages > span ~a').get('href')
                yield Request(url=nextPage)
            except:
                self.logger.info("Next page no more ")


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = soup.select_one('.navi a').text
        item['title'] =  response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('.show_con.fl img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('.show_con.fl p')])
        item['abstract'] = item['body'].split('\n')[0]
        return item