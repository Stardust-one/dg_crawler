import json
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil


# author : 刘鼎谦
class ZaobaoSpider(BaseSpider):
    name = 'zaobao'
    allowed_domains = ['zaobao.com']
    start_urls = ['https://www.zaobao.com/']
    website_id = 1674
    language_id = 1813
    api = 'https://www.zaobao.com/more/sitemap/{0}?pageNo={1}&pageSize={2}'

    def parse(self, response):
        r = BeautifulSoup(response.text, 'html.parser')
        for i in r.select('.nav-item'):
            for j in i.select('.dropdown-item'):
                cate2 = 'https://www.zaobao.com' + j.get('href')
                if re.findall("stock", cate2):
                    continue
                meta = {
                    'category1': i.select_one('a').text,
                    'category2': j.text
                }
                yield Request(url=cate2, meta=meta, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        try:
            sitemapId = re.findall("sitemapId=\"\d+\"", response.text)[0]
            response.meta['id'] = re.findall('\d+', sitemapId)[0]
            for t in [1,2]:
                for i in [18,9,15]:
                    yield Request(url=self.api.format(response.meta['id'], str(t), str(i)), meta=response.meta,
                                  callback=self.parse_page)
        except:
            pass

    def parse_page(self, response):
        # try:
        #     js = json.loads(response.text)
        # except:
        #     yield Request(url=response.url, callback=self.parse_page, meta=response.meta)
        js = json.loads(response.text)
        flag = True
        if self.time is None:
            for i in js['result']['data']:
                url = 'https://www.zaobao.com' + i['url']
                meta = {
                    'pub_time': i['publicationDate'],
                    'title': i['title'],
                    'abstract': i['contentPreview'],
                    'category1': response.meta['category1'],
                    'category2': response.meta['category2']
                }
                yield Request(url=url, meta=meta, callback=self.parse_item)
        else:
            last_pub = js['result']['data'][-1]['publicationDate']
            if self.time < DateUtil.formate_time2time_stamp(last_pub):
                for i in js['result']['data']:
                    url = 'https://www.zaobao.com' + i['url']
                    meta = {
                        'pub_time': i['publicationDate'],
                        'title': i['title'],
                        'contentPreview': i['contentPreview'],
                        'category1': response.meta['category1'],
                        'category2': response.meta['category2']
                    }
                    yield Request(url=url, meta=meta, callback=self.parse_item)
            else:
                self.logger.info("时间截止")
                flag = False
        if flag:
            for i in range(3, js['result']['pageSize'] + 1):
                for j in [18,15,9]:
                    url = self.api.format(response.meta['id'], str(i), str(j))
                    yield Request(url=url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = ''.join(i.text.strip() + '\n' for i in soup.select('#article-body p'))
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = []
        yield item
