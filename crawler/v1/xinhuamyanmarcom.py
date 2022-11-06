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
class XinhuamyanmarcomSpider(BaseSpider):
    name = 'xinhuamyanmarcom'
    #allowed_domains = ['https://xinhuamyanmar.com/']
    start_urls = ['https://xinhuamyanmar.com/']

    website_id = 1459  # 网站的id(必填)
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
    timesAgo=['months','years','month','year']

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-main-menu > li > a')[1:]:
            meta={'category1':i.text}
            yield Request(url=i.get('href'),callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        tt=soup.select('.mvp-blog-story-list.left.relative.infinite-content .mvp-cd-date.left.relative')[0].text
        if tt.split()[1] in self.timesAgo:
            flag=False
            last_pub = '1991-03-10 00:00:00'
        else:
            last_pub = Util.format_time2(tt)
        if self.time is None or (Util.format_time3(last_pub)) >= int(self.time):
            self.logger.info(response.url)
            self.logger.info(tt)
            for i in soup.select('.mvp-blog-story-wrap.left.relative.infinite-post'):
                response.meta['title']= i.select_one('h2').text
                response.meta['pub_time']=Util.format_time2(i.select_one('.mvp-cd-date.left.relative').text.strip())
                url=i.select_one('a').get('href')
                yield Request(url=url, callback=self.parse_item,meta=response.meta)
        else:
            self.logger.info("时间截止")
            self.logger.info(response.url)
            flag = False
        if flag:
            try:
                url=response.url+'page'
                if url.split('page')[1] == '':
                    currentPage='1'
                else:
                    currentPage=response.url.split('page')[1][1:-1]
                nextPage=response.url.split('page')[0]+f"page/{str(int(currentPage)+1)}/"
                yield Request(url=nextPage, callback=self.parse_page,meta=response.meta)
            except:
                self.logger.info("Next page no more ")


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('#mvp-post-feat-img img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('#mvp-content-main p')])
        item['abstract'] = item['body'].split('\n')[1]
        return item