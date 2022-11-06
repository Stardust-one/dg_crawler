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

def time_font_4(past_time):
    #14 Juli 2021, 16:03:12 WIB
    #18 Oktober 2019 - 15:10 WIB
    day = past_time.split(' ')[0]
    month = past_time.split(' ')[1]
    year = past_time.split(' ')[2].strip(',')
    if month == 'Januari':
        month = '01'
    elif month == 'Februari':
        month = '02'
    elif month == 'Maret':
        month = '03'
    elif month == 'April':
        month = '04'
    elif month == 'Mei':
        month = '05'
    elif month == 'Juni':
        month = '06'
    elif month == 'Juli':
        month = '07'
    elif month == 'Agustus':
        month = '08'
    elif month == 'September':
        month = '09'
    elif month == 'Oktober':
        month = '10'
    elif month == 'November':
        month = '11'
    else:
        month = '12'
    return year + '-' + month + '-' + day + ' ' + past_time.split(' ')[4] + ':00'

def time_font_7(past_time):
    return past_time.split('/')[2].split(',')[0] + '-' + past_time.split('/')[1] + '-' + past_time.split('/')[0] + ' ' + past_time.split(' ')[1] + ':00'

#author 陈宣齐
class InsidekompasSpider(BaseSpider):
    name = 'insidekompas'
    website_id =  15 # 网站的id(必填)
    language_id =  1952 # 所用语言的id
    # allowed_domains = ['inside.kompas.com']
    start_urls = ['https://www.kompas.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.find('ul', class_='nav__row clearfix').find_all('a')[:-1]:
            yield Request(url=i.get('href'), meta={'category1':i.text},callback=self.parse_2)

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        img = ''
        abstart = ''
        last_time = ''
        if page_soup.find('div', class_='latest--news mt2 clearfix') is not None:
            if page_soup.find('div', class_='latest--news mt2 clearfix').find('div',
                                                                              class_='article__list clearfix') is not None:
                for i in page_soup.find('div', class_='latest--news mt2 clearfix').find_all('div',
                                                                                            class_='article__list clearfix'):
                    url = i.find('a').get('href')
                    img = i.find('img').get('data-src')
                    title = i.find('div', class_='article__list__title').text.strip('\n')
                    if len(i.find('div', class_='article__date').text.strip().split(' ')) == 3:
                        pub_time = time_font_7(i.find('div', class_='article__date').text)
                    else:
                        pub_time = time_font_4(i.find('div', class_='article__date').text.split(',')[1].strip())
                    last_time = pub_time
                    if self.time == None or Util.format_time3(pub_time) >= int(self.time):  # 截止功能
                        yield Request(url=url,meta={ 'title':title, 'img':img, 'category1':response.meta['category1'], 'pub_time':pub_time},callback=self.parse_3)
                    else:
                        self.logger.info("时间截止")
        if page_soup.find('div', class_='foodLatest clearfix') is not None:
            for i in page_soup.find('div', class_='foodLatest clearfix').find_all('div',
                                                                                  class_='foodLatest__item clearfix'):
                url = i.find('a').get('href')
                img = i.find('img').get('src')
                pub_time = time_font_7(i.find('div', class_='food__date').text)
                last_time = pub_time
                title = i.find('h3', class_='food__title').text.strip('\n')
                if self.time == None or Util.format_time3(pub_time) >= int(self.time):  # 截止功能
                    yield Request(url=url,meta={ 'title':title, 'img':img, 'category1':response.meta['category1'], 'pub_time':pub_time},callback=self.parse_3)
                else:
                    self.logger.info("时间截止")
        if page_soup.find('div', class_='row article__wrap__grid--flex col-offset-fluid') is not None:
            for i in page_soup.find('div', class_='row article__wrap__grid--flex col-offset-fluid').find_all('div',
                                                                                                             class_='article__grid'):
                url = i.find('a').get('href')
                img = i.find('img').get('data-src')
                if i.find('h3', class_='article__title') is not None:
                    title = i.find('h3', class_='article__title').text.strip('\n')
                else:
                    title = i.find('div', class_='article__title').text.strip('\n')
                pub_time = time_font_7(i.find('div', class_='article__date').text)
                last_time = pub_time
                if self.time == None or Util.format_time3(pub_time) >= int(self.time):  # 截止功能
                    yield Request(url=url,meta={ 'title':title, 'img':img, 'category1':response.meta['category1'], 'pub_time':pub_time},callback=self.parse_3)
                else:
                    self.logger.info("时间截止")
        if page_soup.find('div', class_='parapuanLatest clearfix') is not None:
            for i in page_soup.find('div', class_='parapuanLatest clearfix').find_all('div',
                                                                                      class_='parapuanLatest__item clearfix'):
                url = i.find('a').get('href')
                img = i.find('img').get('src')
                pub_time = time_font_7(i.find('div', class_='parapuan__date').text)
                last_time = pub_time
                title = i.find('h3', class_='parapuan__title').text.strip('\n')
                if self.time == None or Util.format_time3(pub_time) >= int(self.time):  # 截止功能
                    yield Request(url=url,meta={ 'title':title, 'img':img, 'category1':response.meta['category1'], 'pub_time':pub_time},callback=self.parse_3)
                else:
                    self.logger.info("时间截止")
        if page_soup.find('a', class_='paging__link paging__link--next') is not None:
            if last_time != '':
                if self.time == None or Util.format_time3(last_time) >= int(self.time):  # 截止功能
                        yield Request(url=page_soup.find('a',class_='paging__link paging__link--next').get('href'),callback=self.parse_2,meta={ 'category1':response.meta['category1']})
                else:
                    self.logger.info("时间截止")

    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text, 'lxml')
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['category1'] = response.meta['category1']
        item['body'] = ''
        item['pub_time'] = response.meta['pub_time']
        for i in new_soup.find('div', class_='read__content').find_all('p'):
            item['body'] += i.text
        item['abstract'] = item['body'].split('.')[0]
        item['category2'] = ''
        yield item