from crawler.spiders import BaseSpider
from datetime import datetime

import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup


# author:刘鼎谦   # 该网站新闻量很少
class MmpeacemonitorSpider(BaseSpider):
    name = 'mmpeacemonitor'
    allowed_domains = ['www.mmpeacemonitor.org']
    start_urls = ['https://www.mmpeacemonitor.org/category/en-interviews',    # 英语
                  'https://www.mmpeacemonitor.org/category/interviews',         # 面条
                  'https://www.mmpeacemonitor.org/category/news']               # 面条

    website_id = 1495   # 网站的id(必填)
    language_id = 1866  # 双语网站，英语和 2065 面条语
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag=True
        last_pub=Util.format_time2(soup.select('.author>li')[-2].text.split(':')[1].replace('th',''))
        all_pub_time=[i.text.split(':')[1].replace('th','') for i in soup.select('.author>li')]
        for i in range(len(all_pub_time)):
            if ' သတင်း ' in all_pub_time:
                all_pub_time.remove(' သတင်း ')
            else:
                break
        if self.time is None or Util.format_time3(last_pub) >= int(self.time):
            j = 0
            for i in soup.select('h2>a'):
                meta={'title':i.text.strip(),'pub_time':Util.format_time2(all_pub_time[j])}
                j+=1
                if re.findall('category/en-interviews', response.url):
                    meta['category1']='en-interviews'
                elif re.findall('category/interviews', response.url):
                    meta['category1']='အင်တာဗျူး'
                else:
                    meta['category1'] = 'သတင်း'
                yield Request(url=i.get('href'), callback=self.parse_item, meta=meta)
        else:
            self.logger.info('时间截止')
            flag=False
        if flag:
            try:
                nextPage=soup.select_one('.next').get('href')
                yield Request(url=nextPage)
            except:
                self.logger.info("next page no more")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        if response.meta['category1'] == 'en-interviews':
            self.language_id=1866
        else:
            self.language_id=2065
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('.blog-post img')]
        item['pub_time'] = response.meta['pub_time']   # 只能转换英文的，缅甸语的默认为当前时间
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('.blog-post p')])
        item['abstract'] = soup.select_one('.blog-post p').text
        return item

