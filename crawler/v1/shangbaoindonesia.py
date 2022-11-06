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

def time_font_6(past_time):
    #2021年 07月 07日 20:35 PM
    # %Y-%m-%d %H:%M:%S
    year = past_time.split(" ")[0].strip("年")
    month = past_time.split(" ")[1].strip("月")
    day = past_time.split(" ")[2].strip("日")
    small_time = past_time.split(" ")[3] + ":00"
    return year + '-' + month + '-' + day + ' ' + small_time

#author 陈宣齐
class shangbaoindonesia(BaseSpider):
    name = 'shangbaoindonesia'
    website_id = 10 # 网站的id(必填)
    language_id = 1813 # 所用语言的id
    start_urls = ['http://www.shangbaoindonesia.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.find('ul', class_='nav navbar-nav').find_all('li')[1:]:
            yield Request(url=i.find('a').get('href'),callback=self.parse_2,meta={'category1':i.find('a').text})

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        last_time = ''
        if page_soup.find('ul', class_='catg-nav catg-nav3') is not None:
            for i in page_soup.find('ul', class_='catg-nav catg-nav3').find_all('div', class_='row mt5 mr5'):
                for a in i.find_all('div', class_='col-xs-6'):
                    url = a.find('a').get('href')
                    title = a.find('div', class_='right').find('a').text
                    pub_time = time_font_6(a.find('div', class_='right').find('p').text.strip(' '))
                    last_time = pub_time
                    img = a.find('img').get('src')
                    if self.time == None or Util.format_time3(last_time) >= int(self.time):  # 截止功能
                        yield Request(url,callback=self.parse_3,meta={'title':title,'pub_time':pub_time,'img':img,'category1':response.meta['category1']})
                    else:
                        self.logger.info('时间截至')
        if page_soup.find("ul", class_='pagination') is not None:
            if page_soup.find("ul", class_='pagination').find('li', class_='right') is not None:
                if last_time != '':
                    if self.time == None or Util.format_time3(last_time) >= int(self.time):  # 截止功能
                        yield Request(url=page_soup.find("ul",class_='pagination').find('li',class_='right').find('a').get('href'),callback=self.parse_2,meta={'category1':response.meta['category1']})
                    else:
                        self.logger.info('时间截至')

    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text,'lxml')
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['category1'] = response.meta['category1']
        item['body'] = ''
        # item['pub_time'] = pub_time
        # item['abstract'] = abstract
        item['body'] = ''
        item['pub_time'] = response.meta['pub_time']
        for i in new_soup.find('div', id='talkifyRoot', class_='post-content').find_all('p'):
            item['body'] += i.text
        item['abstract'] = item['body'].split('。')[0]
        yield item