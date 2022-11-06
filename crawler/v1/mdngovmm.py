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
class MdngovmmSpider(BaseSpider):
    name = 'mdngovmm'
    allowed_domains = ['www.mdn.gov.mm']
    start_urls = ['http://www.mdn.gov.mm/']

    website_id = 1492  # 网站的id(必填)
    language_id = 2065  # 缅甸语言
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
          
        

    noNews = ['http://www.mdn.gov.mm/my/video-demand', 'http://www.mdn.gov.mm/my/live',
              'http://www.mdn.gov.mm/my/video', 'http://www.mdn.gov.mm/index.php/newspaper/public',
              'http://www.mdn.gov.mm/index.php/my/home','http://www.mdn.gov.mm/my/ethnic-affairs']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.gva-navigation>ul>li')[1:-1]:
            cat1=i.select_one('a').text
            cat1_url='http://www.mdn.gov.mm'+i.select_one('a').get('href')
            if cat1_url in self.noNews:
                continue
            yield Request(url=cat1_url,callback=self.parse_more,meta={'category1':cat1,'category2':None})
            for j in i.select('a'):
                cat2=j.text
                cat2_url='http://www.mdn.gov.mm'+j.get('href')
                yield Request(url=cat2_url,callback=self.parse_more,meta={'category1':cat1,'category2':cat2})

    def parse_more(self, response):  # 动态翻页
        soup = BeautifulSoup(response.text, 'html.parser')
        last_pub = Util.format_time2(soup.select('.post-content .post-created')[0].text)
        last_pub_stamp = Util.format_time3(last_pub)
        self.logger.info(last_pub)
        flag = True
        if self.time is None or last_pub_stamp >= int(self.time):
            for i in soup.select('.block-content .post-content')[:-5]:
                try:
                    response.meta['title'] = i.select_one('.post-title').text.strip()
                except:
                    continue
                url = 'http://www.mdn.gov.mm' + i.select_one('.post-title a').get('href')
                response.meta['pub_time'] = Util.format_time2(soup.select_one('.post-created').text)
                yield Request(url=url, callback=self.parse_item, meta=response.meta)
        else:
            self.logger.info('时间截止.')
            flag = False
        if flag:
            try:
                nextPage = response.url.split('?')[0] + soup.select_one('.pager__item.pager__item--next a').get('href')
                yield Request(url=nextPage, callback=self.parse_more, meta=response.meta)
            except:
                self.logger.info("Next page no more")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('.post-content img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = response.meta['category2']
        try:
            item['body'] = '\n'.join([i.text.strip() for i in soup.select('.post-content p')])
            item['abstract'] = soup.select_one('.post-content p').text.strip()
            return item
        except:
            pass

