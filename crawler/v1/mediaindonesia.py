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
    #Minggu 25 Juli 2021, 10:42 WIB
    day = past_time.split(' ')[1]
    month = past_time.split(' ')[2]
    year = past_time.split(' ')[3].strip(',')
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

#author 陈宣齐
class MediaindonesiaSpider(BaseSpider):
    name = 'mediaindonesia'
    website_id =  17 # 网站的id(必填)
    language_id = 1952 # 所用语言的id
    # allowed_domains = ['mediaindonesia.com']
    start_urls = ['https://mediaindonesia.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.find('ul', class_='the-menu').find_all('li')[1:]:
            if i.find('a').get('href') != '#':
                yield Request(url=i.find('a').get('href'),callback=self.parse_2,meta={'category1':i.find('a').text})

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        img = ''
        abstart = ''
        last_time = ''
        if page_soup.find('div', id='web', class_='block-content').find_all('div', class_='article-big') is not None:
            for i in page_soup.find('div', id='web', class_='block-content').find_all('div', class_='article-big'):
                new_url = i.find('a').get('href')
                img = i.find('img').get('data-original')
                title = i.find('div', class_='article-content').find('a').text.strip('\n')
                if i.find('div', class_='article-content').find('p') is not None:
                    abstart = i.find('div', class_='article-content').find('p').text
                pub_time = time_font_4(i.find('span', class_='meta').find_all('a')[-1].text.strip('🕔'))
                last_time = pub_time
                if self.time == None or Util.format_time3(pub_time) >= int(self.time):  # 截止功能
                    yield Request(url=new_url,callback=self.parse_3,meta={'title':title,'abstract':abstart,'img':img,'pub_time':pub_time,'category1':response.meta['category1']})
                else:
                    self.logger.info("时间截止")
        if page_soup.find('div',class_='pagination') is not None:
            if page_soup.find('div', class_='pagination').find('a', rel='next') is not None:
                if self.time == None or Util.format_time3(last_time) >= int(self.time):  # 截止功能
                    yield Request(url=page_soup.find('div',class_='pagination').find('a',rel='next').get('href'),callback=self.parse_2,meta={'category1':response.meta['category1']})

    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text, 'lxml')
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['body'] = ''
        item['pub_time'] = response.meta['pub_time']
        if new_soup.find('div', style='line-height: 1.6;', itemprop="articleBody"):
            item['body'] = new_soup.find('div', style='line-height: 1.6;', itemprop="articleBody").text.strip('\n')
            if response.meta['abstract'] == '':
                item['abstract'] = item['body'].split('.')[0]
            else:
                item['abstract'] = response.meta['abstract']
        self.logger.info("-------------------------------------------------------------------------------")
        yield item