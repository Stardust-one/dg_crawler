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
import glob
import json

def time_font_3(past_time):
    #24 Jun, 2021
    # %Y-%m-%d %H:%M:%S
    day = past_time.split(' ')[0].strip('\n')
    month = past_time.split(' ')[1].strip(',')
    year = past_time.split(' ')[2]
    if month == 'JAN':
        month = '01'
    elif month == 'FEB':
        month = '02'
    elif month == 'MAR':
        month = '03'
    elif month == 'APR':
        month = '04'
    elif month == 'MAY':
        month = '05'
    elif month == 'JUN':
        month = '06'
    elif month == 'JUL':
        month = '07'
    elif month == 'AUG':
        month = '08'
    elif month == 'SEP':
        month = '09'
    elif month == 'OCT':
        month = '10'
    elif month == 'NOV':
        month = '11'
    else:
        month = '12'
    return year + '-' + month + '-' + day + ' 00:00:00'


# author 黄金盛
class Jtm(BaseSpider):
    name = 'jtm'
    allowed_domains = ['jtm.com.mo']
    start_urls = ['https://jtm.com.mo']
    website_id = 672  # 网站的id(必填)
    language_id = 2122  # 所用语言的id
    sql = {  # my sql 配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')  # 这是什么解析方式？
        for i in soup.select('li>a')[0:7]:
            yield Request(url=i.get('href'),callback=self.parse_page,meta={'category1':i.text})
        #最后一页比较特殊需要特殊处理
        yield Request(url=soup.select('li>a')[-1].get('href'),callback=self.parse_page_special,meta={'category1':soup.select('li>a')[-1].text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find('div', id='left_column').find_all('div', class_='loop-entry clear'):
            news_url = a.find('a').get('href')
            img = a.find('img').get('src')
            title = a.find('div',class_='loop-entry-right').find('a').get('title')
            abstract = a.find('div', class_='loop-entry-right').text.strip('\n')
            news_time = time_font_3(a.find('div',class_='loop-entry-date').text)
            yield Request(url=news_url,callback=self.parse_3,meta={'img':img,'category1':response.meta['category1'],'title':title,'pub_time':news_time,'abstract':abstract})
        last_time = time_font_3(soup.find('div', id='left_column').find_all('div', class_='loop-entry clear')[-1].find('div',class_='loop-entry-date').text)
        if soup.find('a',class_='page_next') is not None:
            if self.time == None or Util.format_time3(last_time) >= int(self.time):
                yield Request(soup.find_all('a',class_='page_next')[-1].get('href'),callback=self.parse_page,meta={'category1':response.meta['category1']})
        else:
            if self.time == None or Util.format_time3(last_time) >= int(self.time):
                for i in soup.find('div',class_='container clear').find_all('a'):
                    yield Request(i.get('href'),callback=self.parse_page,meta={'category1':response.meta['category1']})


    def parse_page_special(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        for i in soup.find('div', id='left_column').find_all('a'):
            yield Request(url=i.get('href'),callback=self.parse_page,meta={'category1':response.meta['category1']})

    def parse_3(self,response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['body'] = ''
        for i in soup.find('div',align='justify').find_all('p'):
            item['body'] += i.text.strip('\n').strip(' ')
        yield item
