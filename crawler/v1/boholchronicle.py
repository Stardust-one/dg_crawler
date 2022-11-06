from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time


class BoholchronicleSpider(BaseSpider):
    name = 'boholchronicle'
    website_id = 448 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://www.boholchronicle.com.ph/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('#menu-item-45526 .sub-menu li a'):
            yield Request(i.attrs['href'],meta={'category1':'News','category2':i.text},callback=self.parse2)
        for i in html.select('#menu-item-45298 .sub-menu li a'):
            yield Request(i.attrs['href'],meta={'category1':'Commentary','category2':i.text},callback=self.parse2)
        for i in html.select('#menu-item-5348 .sub-menu li a'):
            yield Request(i.attrs['href'],meta={'category1':'Features','category2':i.text},callback=self.parse2)
        yield Request(html.select('#menu-item-5349 a')[0].attrs['href'],meta={'category1':'Nation','category2':None},callback=self.parse2)

    def parse2(self, response):
        html = BeautifulSoup(response.text)
        # 遍历此页所有文章
        for i in html.select('#loop-container div .post-title a'):
            yield Request(i.attrs['href'],meta=response.meta,callback=self.parse3)
        # 下面这里就是截止方法
        # time_为此页最后一篇文章的发布时间
        time_ = Util.format_time3(Util.format_time2(html.select('#loop-container div .post-byline')[-1].text))
        # 时间判断，继续爬取下一页的条件是time为None或者time_大于time
        if self.time == None or time_ >= int(self.time):
            # 爬取下一页
            yield Request(html.select('.nav-links > a')[-1].attrs['href'],meta=response.meta,callback=self.parse2)

    def parse3(self, response):
        html = BeautifulSoup(response.text)
        item = NewsItem()
        item['title'] = html.select('.post-title')[0].text
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = ''
        for i in html.select('.heateorSssClear ~ p'):
            item['body'] += (i.text+'\n')
        if html.select('.heateorSssClear ~ p') != []:
            item['abstract'] = html.select('.heateorSssClear ~ p')[0].text
        item['pub_time'] = Util.format_time2(html.select('.post-title ~ .post-byline')[0].text)
        if html.select('#loop-container img') != []:
            item['images'] = [html.select('#loop-container img')[0].attrs['src'],]
        yield item
