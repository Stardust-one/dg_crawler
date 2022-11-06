from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
import requests

# author 曾嘉祥
class efeSpider(BaseSpider):
    name = 'efeSpider'
    allowed_domains = ['efe.com']
    start_urls = ['https://www.efe.com/efe/espana/1']
    website_id = 899  # 网站的id(必填)
    language_id = 2181  # 所用语言的id
    sql = {  # sql配置
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
        soup = BeautifulSoup(response.text, 'html.parser')
        menu=soup.find(class_='efe-menu-secciones dropdown').select('li a')
        del menu[0]
        for i in menu:
            meta = {'category1': i.text, 'category2': None, 'title': None, 'abstract': None, 'images': None}
            url = ('https://www.efe.com/' + i.get('href'))
            yield Request(url,callback=self.parse_category,meta=meta)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu=soup.select_one('ul.lista')
        for i in menu.select('li'):  # 该目录初始的文章
            url = 'https://www.efe.com/' + i.select_one('a').get('href')
            # response.meta['title'] = i.select_one('font').text
            response.meta['images'] = ['https:'+i.select_one('img').get('data-original')]
            response.meta['category2']=i.select_one('span.guia').text
            yield Request(url=url, meta=response.meta, callback=self.parse_detail)

        time_url = 'https://www.efe.com/' + menu.select_one('li a').get('href')
        r = requests.get(time_url)
        time_soup = BeautifulSoup(r.text, 'html.parser')
        time = time_soup.select_one('time').get('datetime')
        pub_time = time.replace('T', ' ')
        adjusted_time = pub_time.replace('Z', '')
        if self.time is None or Util.format_time3(adjusted_time) >= int(self.time):
            try:
                nextPage = 'https://www.efe.com/' + soup.select_one("li.next a").get('href')
                yield Request(nextPage, callback=self.parse_category, meta=response.meta)
            except:
                self.logger.info('Next page no more!')
        else:
            self.logger.info('时间截止')

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('h1.titulo').text
        time=soup.select_one('time').get('datetime')
        pub_time = time.replace('T',' ')
        pub_time = pub_time.replace('Z', '')
        item['pub_time'] = pub_time
        item['images'] = response.meta['images']
        p_list = []
        if soup.find('div', class_="texto dont-break-out").select('p'):
            all_p = soup.find('div', class_="texto dont-break-out").select('p')
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
            item['abstract'] = p_list[0]
            item['body'] = body
        return item