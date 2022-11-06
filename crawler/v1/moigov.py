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


# author:刘鼎谦    # 突然就有5秒盾了？
class MoigovSpider(BaseSpider):
    name = 'moigov'
    #allowed_domains = ['moi.gov.mm/npe']
    start_urls = ['https://www.moi.gov.mm/npe/news']

    website_id = 1406  # 网站的id(必填)
    language_id = 2065  # 缅甸语言
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

    base_url = 'https://www.moi.gov.mm'
    getTagDic = {
        'news':'news',
        'announcements':'anoun',
        'article':'article',
        'editor-remark':'editor'
    }
    
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#main-menu > li')[1:]:
            meta={}
            meta['category1'] = i.select_one('a').text
            meta['category2'] = None
            meta['page']='0'
            meta['tag'] = self.getTagDic[f'{i.select_one("a").get("href").split("/")[-1]}']
            yield Request(url=self.base_url+i.select_one('a').get('href'), meta=meta,callback=self.parse_page)
            for j in i.select('li > a'):
                meta['category2'] = j.text
                yield Request(url=self.base_url + j.get('href'),callback=self.parse_page,meta=meta)

    def getFormatTime(self, rtime):
        t = re.findall('\d+/\d+/\d+',rtime)[0]
        tt = "{0}-{1}-{2}".format(t[6:],t[:2],t[3:5]) + rtime.split('-')[1]+":00"
        return tt

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        last_pub_time = self.getFormatTime(soup.select(f'.{response.meta["tag"]}-created')[-1].text)
        if self.time is None or Util.format_time3(last_pub_time) >= int(self.time):
            for i in soup.select('.news-container'):
                response.meta['title'] = i.select_one(f'.{response.meta["tag"]}-title').text.strip()
                response.meta['pub_time'] = self.getFormatTime(i.select_one(f'.{response.meta["tag"]}-created').text)
                yield Request(url=self.base_url+i.select_one(f'.{response.meta["tag"]}-title a').get('href'),meta=response.meta,callback=self.parse_item)
        else:
            flag = False
            self.logger.info('时间截止')

        if flag:
            response.meta['page'] = str(int(response.meta['page'])+1)
            ca = response.url.split('?')[0]   # 去掉末尾的?page=\d+
            cat = ca.split('/')[4] if len(ca.split('/'))== 5 else ca.split('/')[4]+'/'+ ca.split('/')[-1]
            url = self.base_url+f'/npe/{cat}?page='+response.meta['page']
            yield Request(url=url, callback=self.parse_page,meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = ['https://www.moi.gov.mmi'+i.get('src') for i in  soup.select('.content_layout img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = response.meta['category2']
        try:
            item['body'] = ''.join(i.text.strip() + '\n' for i in
                                   soup.select('.node__content p'))
            item['abstract'] = soup.select('.node__content p')[0].text.strip()    # 有部分文章的正文（摘要）在div标签下
        except:
            item['body'] = ''.join(i.text.strip() + '\n' for i in
                                   soup.select('.node__content div'))
            item['abstract'] = soup.select('.node__content div')[0].text.strip()
        return item