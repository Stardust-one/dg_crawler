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
    return year + '-' + month + '-' + day + ' ' + past_time.split(' ')[3]

#author 陈宣齐
class jawapos(BaseSpider):
    name = 'jawapos'
    website_id = 4 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['http://www.jawapos.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        page_url = ['https://www.jawapos.com/nasional/','https://www.jawapos.com/ibu-kota-baru/',
                    'https://www.jawapos.com/bersama-lawan-covid-19/','https://www.jawapos.com/entertainment/',
                    'https://www.jawapos.com/berita-sekitar-anda/','https://www.jawapos.com/sepak-bola/sepak-bola-indonesia/',
                    'https://www.jawapos.com/surabaya/','https://www.jawapos.com/jabodetabek/']
        for i in page_url:
            yield Request(url=i,callback=self.parse_2)
        term = ['117875', '357924', '380697', '117892', '117878', '318448', '318449']
        post_url = 'https://www.jawapos.com/desktop-get-posts/'
        for a in term:
            Data = {
                'post_type[0]': 'post',
                'post_type[1]': 'radar',
                'per_page': '15',
                'taxonomy': 'category',
                'terms': a,
                'security': '7d28825fa6',
                'page_no': '2'
            }
            yield scrapy.FormRequest(url=post_url,formdata=Data,callback=self.parse_post,meta={'page':2,'term':i})

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text,'lxml')
        for i in page_soup.find('div', class_='post-list__container').find_all('div', class_='post-list__item'):
            img = i.find('img').get('data-src')
            title = i.find('a').get('title')
            news_url = i.find('a').get('href')
            abstract = ''
            pub_time = time_font_4(i.find('div', class_='post-list__time').text)
            category1 = i.find('div', class_='post-list__cat').text.strip(' ')
            if i.find('div', class_='post-list__excerpt') is not None:
                abstract = i.find('div', class_='post-list__excerpt').text
            if self.time == None or Util.format_time3(pub_time) >= int(self.time):
                yield Request(url=news_url,callback=self.parse_3,meta={'img':img,'title':title,'pub_time':pub_time,'abstract':abstract,'category1':category1})
            else:
                self.logger.info("时间截止")


    def parse_post(self,response):
        post_url = 'https://www.jawapos.com/desktop-get-posts/'
        page = response.meta['page'] + 1
        rep = json.loads(response.text)
        page_soup = BeautifulSoup(rep['posts'],'lxml')
        last_time = ''
        for i in page_soup.find_all('div', class_='post-list__item'):
            title = i.find('h3', class_='post-list__title').text
            news_url = i.find('h3', class_='post-list__title').find('a').get('href')
            img = i.find('img').get('data-src')
            pub_time = time_font_4(i.find('div', class_='post-list__time').text)
            abstract = i.find('div', class_='post-list__excerpt').text.strip('\n')
            last_time = pub_time
            category1 = i.find('a',class_='category text-uppercase').text.strip('						').strip('\n').strip('						')
            if self.time == None or Util.format_time3(pub_time) >= int(self.time):
                yield Request(url=news_url, callback=self.parse_3,
                              meta={'img': img, 'title': title, 'pub_time': pub_time, 'abstract': abstract,
                                    'category1': category1})
            else:
                self.logger('时间截止')
                return
        if self.time == None or Util.format_time3(last_time) >= int(self.time):
            Data = {
                'post_type[0]': 'post',
                'post_type[1]': 'radar',
                'per_page': '15',
                'taxonomy': 'category',
                'terms': response.meta['term'],
                'security': '7d28825fa6',
                'page_no': '%d' % page
            }
            yield scrapy.FormRequest(url=post_url,formdata=Data,callback=self.parse_post,meta={'term':response.meta['term'],'page':page})

    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text, 'lxml')
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['abstract'] = response.meta['abstract']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['body'] = ''
        if new_soup.find('div',itemprop='articleBody',class_='content') is not None:
            for i in new_soup.find('div',itemprop='articleBody',class_='content').find_all('p'):
                item['body'] += i.text.strip('\n')
        if item['body'] != '':
            yield item
