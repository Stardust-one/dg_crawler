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


def time_font_2(past_time):
    #Mar 29, 2021
    year = past_time.split(' ')[2]
    day = past_time.split(' ')[1].strip(',')
    month = past_time.split(' ')[0]
    if month == 'Jan':
        month = '01'
    elif month == 'Feb':
        month = '02'
    elif month == 'Mar':
        month = '03'
    elif month == 'Apr':
        month = '04'
    elif month == 'May':
        month = '05'
    elif month == 'Jun':
        month = '06'
    elif month == 'Jul':
        month = '07'
    elif month == 'Aug':
        month = '08'
    elif month == 'Sep':
        month = '09'
    elif month == 'Oct':
        month = '10'
    elif month == 'Nov':
        month = '11'
    else:
        month = '12'
    return year + '-' + month + '-' + day + ' 00:00:00'

# author 陈宣齐
class insideindonesia(BaseSpider):
    name = 'insideindonesia'
    website_id = 1 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://www.insideindonesia.org/topics/tags']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }


    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        news_soup = BeautifulSoup(response.text, 'lxml')
        for i in news_soup.find('ul', class_='tag-list').find_all('li'):
            category = i.find('a').text.strip('\n').strip('				')
            page_url = 'https://www.insideindonesia.org/' + i.find('a').get('href')
            yield Request(page_url,callback=self.parse_2,meta={'category':category})

    def parse_2(self,response):
        page = BeautifulSoup(response.text, 'lxml')
        for i in page.find_all('article', class_='item'):
            title = i.find('header', class_='article-header clearfix').find('a').text.strip('\n').strip(
                '				')
            news_url = 'https://www.insideindonesia.org/' + i.find('header', class_='article-header clearfix').find(
                'a').get('href')
            news_time = time_font_2(i.find('dd', class_='published').text.strip('\n').strip('				'))
            img = ''
            if i.find('img') is not None:
                img = 'https://www.insideindonesia.org/' + i.find('img').get('src')
            yield Request(news_url,callback=self.parse_3,meta={'title':title,'pub_time':news_time,'img':img,'category':response.meta['category']})

        last_time = time_font_2(
            page.find_all('article', class_='item')[-1].find('dd', class_='published').text.strip('\n').strip(
                '				'))
        if page.find('ul', class_='pagination') is not None:
            next_page = 'https://www.insideindonesia.org/' + page.find('ul', class_='pagination').find_all('li')[
                -2].find('a').get('href')
            if self.time == None or Util.format_time3(last_time) >= int(self.time):
                yield Request(next_page,callback=self.parse_2,meta={'category':response.meta['category']})

    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text, 'lxml')
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['body'] = ''
        item['abstract'] = ''
        item['category1'] = response.meta['category']
        item['category2'] = ''
        if len(new_soup.find('section', class_='article-content clearfix articlePushRight').find_all('p')) > 0:
            item['abstract'] =new_soup.find('section', class_='article-content clearfix articlePushRight').find_all('p')[0].text
            for i in new_soup.find('section', class_='article-content clearfix articlePushRight').find_all('p'):
                item['body'] += i.text.strip('\n').strip('\xa0')
            yield item

