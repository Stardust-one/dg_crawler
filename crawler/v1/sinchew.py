from crawler.spiders import BaseSpider
# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
import requests
from datetime import datetime
import json

#author 陈宣齐
class SinchewSpider(BaseSpider):
    name = 'sinchew'
    website_id =  13 # 网站的id(必填)
    language_id =  1813 # 所用语言的id
    allowed_domains = ['sinchew.com.my']
    start_urls = ['https://www.sinchew.com.my/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.select('.dropdownlistbylist > a'):
            yield Request(url=i.get('href'),callback=self.parse_2,meta={'category1':i.text})

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        img = ''
        abstract = ''
        last_time = ''
        if page_soup.find('div', id='articlenum',style='width:670px;text-align:left;float:left;margin-top:30px;') is not None:
            for i in page_soup.select('div #articlenum > li'):
                new_url = i.find('a').get('href')
                title = i.find('div', style='font-size:20px;').text
                abstract = i.find('div', style='font-size:15px;padding-top:5px;').text
                if i.find('img') is not None and i.find('img').get('src') != '/pagespeed_static/1.JiBnMqyl6S.gif':
                    img = i.find('img').get('src')
                pub_time = i.find('div', id='time').text
                last_time = pub_time
                if self.time == None or Util.format_time3(pub_time) >= int(self.time):
                    yield scrapy.Request(new_url.strip(),callback=self.parse_3,meta={'category1':response.meta['category1'],'title':title,'pub_time':pub_time,'abstract':abstract,'img':img})
                else:
                    self.logger.info("时间截止")
        if page_soup.find('li', class_='page-next') is not None:
            if self.time == None or Util.format_time3(last_time) >= int(self.time):
                yield Request(url=page_soup.find('li', class_='page-next').find('a').get('href').strip(),callback=self.parse_2,meta={'category1':response.meta['category1']})
            else:
                self.logger.info("时间截至")


    def parse_3(self,response):
        new_soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['body'] = ''
        for i in new_soup.find('div', id='dirnum').find_all('p'):
            item['body'] += i.text
        if response.meta['abstract'] == '':
            item['abstract'] = item['body'].split('。')[0]
        else:
            item['abstract'] = response.meta['abstract']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item
