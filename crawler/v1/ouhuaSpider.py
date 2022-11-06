from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
import requests

# author: 曾嘉祥
class ouhuaSpider(BaseSpider):
    name = 'ouhuaSpider'
    allowed_domains = ['ouhua.info']
    start_urls = ['http://www.ouhua.info']
    website_id = 1278  # 网站的id(必填)
    language_id = 1813  # 所用语言的id
    sql = {  # my sql 配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    
          
        

    def parse(self, response):
        # response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        menu=soup.find(class_='nav_navcon left').select('a')
        for i in menu:
            meta = {'category1': i.text, 'category2': None, 'title': None, 'abstract': None, 'images': None}
            url = ('http://www.ouhua.info' + i.get('href'))
            if url == 'http://www.ouhua.info/ohhd-more/index.shtml' or url == 'http://www.ouhua.info//videos.elmandarin.es/':
                continue
            yield Request(url,callback=self.parse_category,meta=meta)

    def parse_category(self, response):
        # response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        # menu = soup.find(class_='branch_list_ul paging')
        menu = soup.find(class_='branch_list_ul paging').select('.tplist_left')
        for i in menu:
            response.meta['abstract'] = i.select_one('div.tplis_txt p').text
            response.meta['images'] = ['https:/' + i.select_one('div.tplist_pic img').get('src')]
            temp_time= i .select_one('div.tplis_txt div.ly').text[-10:]
            adjusted_time=temp_time+' 00:00:00'
            if self.time is None or Util.format_time3(adjusted_time) >= int(self.time):
                url = 'http://www.ouhua.info' + i.select_one('div.tplist_pic a').get('href')
                yield Request(url=url, meta=response.meta , callback=self.parse_detail)
            else:
                self.logger.info("时间截止")
                break

        # if menu.select('div.tplist_pic'):
        #     for i in menu.select('div.tplist_pic'):
        #         url = 'http://www.ouhua.info' + i.select_one('a').get('href')
        #         yield Request(url=url, meta=response.meta, callback=self.parse_detail)

    def parse_detail(self, response):
        # response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('h1').text
        item['abstract'] = response.meta['abstract']

        time=soup.select_one('div.conleft p').text
        pub_time = time[:17]
        pub_time = pub_time.replace('年','-')
        pub_time = pub_time.replace('月', '-')
        pub_time = pub_time.replace('日', '')
        pub_time += ':00'
        item['pub_time'] = pub_time
        # adjusted_time = pub_time
        # if self.time is None or Util.format_time3(adjusted_time) < int(self.time):
        #     self.logger.info('时间截止')
        #     return

        item['images'] =  response.url[:32] + soup.select_one('div.con_content img').get('src')
        p_list = []
        if soup.select('div.con_content p'):
            all_p = soup.select('div.con_content p')
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
            # item['abstract'] = p_list[0]
            item['body'] = body
        return item
