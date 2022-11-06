import random

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


# author:刘鼎谦
class IrrawaddySpider(BaseSpider):
    name = 'irrawaddy'
    allowed_domains = ['www.irrawaddy.com']
    start_urls = ['https://www.irrawaddy.com/category/news',
                  'https://www.irrawaddy.com/category/opinion'
                  'https://www.irrawaddy.com/category/elections',
                  'https://www.irrawaddy.com/category/elections-in-history',
                  'https://www.irrawaddy.com/category/business',
                  'https://www.irrawaddy.com/category/specials/myanmar-covid-19', ]
    website_id = 1472  # 网站的id(必填)
    language_id = 1866

    proxy = random.choice(['01','02'])
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
    url_api = 'https://www.irrawaddy.com/wp-admin/admin-ajax.php'

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        meta = {'category1': response.url.split('/')[4], 'category2': None}
        if meta['category1'] != 'specials':
            meta['offset'] = '0'
            meta['cat'] = soup.select_one('body').get('class')[3].split('-')[1],
            meta['posts[]'] = soup.select_one('.container article').get('class')[0].split('-')[1]
            yield FormRequest(url=self.url_api, formdata={
                'action': 'irr_load_more_articles',
                'offset': '0',
                'cat': meta['cat'],
                'posts[]': meta['posts[]']
            }, callback=self.parse_more, meta=meta)
        else:
            meta['category2'] = 'myanmar-covid-19'
            meta['query_paged'] = '1'
            yield FormRequest(url=response.url, formdata={
                'filter_mood': 'all',
                'filter_date': '1y',
                'date_after': '',
                'date_before': '',
                'date_year': '2012',
                'query_paged': '1',  # 除此之外是无效参数
                'next_page': '',
            }, callback=self.parse_more, meta=meta)

    def get_last_pub(self, url):
        DEFAULT_REQUEST_HEADERS = {
            ':authority':'www.irrawaddy.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
        }
        r = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        tt = soup.select_one('#feeder-articles .date').text.split()
        ttt = "{} {} {}".format(tt[1], tt[0], tt[2])
        pub_time = Util.format_time3(Util.format_time2(ttt))
        return pub_time

    def parse_more(self, response):  # 动态翻页
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        if self.time is None:
            articles = [a.get('href') for a in soup.select('.title a')]
            for article in articles:
                yield Request(article, callback=self.parse_item, meta=response.meta)
        else:
            if self.get_last_pub(soup.select('.title a')[-1].get('href')) >= int(self.time):
                articles = [a.get('href') for a in soup.select('.title a')]
                for article in articles:
                    yield Request(article, callback=self.parse_item, meta=response.meta)
            else:
                self.logger.info('时间截止.')
                flag = False
        if flag:
            if response.meta['category2'] is None:
                response.meta['offset'] = str(int(response.meta['offset']) + 6)
                yield FormRequest(url=self.url_api, formdata={
                    'action': 'irr_load_more_articles',
                    'offset': response.meta['offset'],
                    'cat': response.meta['cat'],
                    'posts[]': response.meta['posts[]']
                }, callback=self.parse_more, meta=response.meta)
            else:
                response.meta['query_paged'] = str(int(response.meta['query_paged']) + 1)
                yield FormRequest(url=response.url, formdata={
                    'filter_mood': 'all',
                    'filter_date': '1y',
                    'date_after': '',
                    'date_before': '',
                    'date_year': '2012',
                    'query_paged': response.meta['query_paged'],  # 除此之外是无效参数
                    'next_page': '',
                }, callback=self.parse_more, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1').text
        item['images'] = [soup.select_one('article figure').get('style')[22:-2]]
        tt = soup.select_one('#feeder-articles .date').text.split()
        ttt = "{} {} {}".format(tt[1], tt[0], tt[2])
        item['pub_time'] = Util.format_time2(ttt)
        item['category2'] = response.meta['category2']
        item['body'] = ''.join(i.text.strip() + '\n' for i in soup.select('.article-entry p'))
        item['abstract'] = soup.select_one('.article-entry  p').text
        return item
