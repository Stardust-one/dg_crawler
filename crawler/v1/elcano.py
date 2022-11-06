from crawler.spiders import BaseSpider
# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from datetime import datetime
import time
import re
import requests

# author: 曾嘉祥
class elcano(BaseSpider):
    name = 'elcano'
    allowed_domains = ['realinstitutoelcano.org']
    start_urls = ['http://www.realinstitutoelcano.org/wps/portal/rielcano_es']
    website_id = 792  # 网站的id(必填)
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
        menu = soup.find(class_='nav-collapse collapse').select('.dropdown-menu')[1]
        for i in menu.select('li a'):
            meta = {'category1': i.text, 'category2': None, 'title': None, 'abstract': None, 'images': None}
            url = ('http://www.realinstitutoelcano.org' + i.get('href'))
            yield Request(url,callback=self.parse_category,meta=meta)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.find(class_='main-content keepspan8')
        flag = True
        hrefs = []
        times = []
        abstracts = []
        for i in menu.select('h1'):  # 该目录初始的文章
            hrefs.append(i.select_one('a').get('href'))
        hrefs = [x.strip() for x in hrefs if x.strip() != '']
        for i in menu.select('h2'):
            times.append(i.text)
        for i in menu.find_all(dir='ltr'):
            abstracts.append(i.text)
        for i in range(len(hrefs)):
            try:
                response.meta['abstract'] = abstracts[i]
            except:
                response.meta['abstract'] = None
            try:
                adjusted_time = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", times[i].strip()).group(0)
            except:
                adjusted_time='1/1/2021'
            adjusted_time = adjusted_time.split('/')[2] + '-' + adjusted_time.split('/')[1] + '-' + adjusted_time.split('/')[0] + ' 00:00:00'
            response.meta['time'] = adjusted_time
            if self.time is None or Util.format_time3(adjusted_time) >= int(self.time):
                url = ('http://www.realinstitutoelcano.org' + hrefs[i])
                yield Request(url=url, meta=response.meta , callback=self.parse_detail)
            else:
                flag = False
                self.logger.info("时间截止")

        if flag:
            try:
                nextPage = 'http://www.realinstitutoelcano.org'+ soup.select_one('.pagination').select('li')[-2].select_one('a').get('href')
                yield Request(nextPage,callback=self.parse_category,meta=response.meta)

            except:
                self.logger.info('Next page no more!')

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['abstract'] = response.meta['abstract']
        item['title'] = soup.select_one('h1.post-title').text
        item['pub_time'] = response.meta['time']
        p_list = []
        if soup.select_one('.post-content').find_all(dir='ltr'):
            all_p = soup.select_one('.post-content').find_all(dir='ltr')
            for paragraph in all_p:
                p_list.append(paragraph.text.strip())
            body = '\n'.join(p_list)
            item['body'] = body
        return item