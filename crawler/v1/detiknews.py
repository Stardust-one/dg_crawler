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


def time_font_2(past_time):
    #Sabtu, 24 Jul 2021 17:27
    #Sabtu, 29 Mei  2021 11:24 WIB
    if past_time.split(' ')[3] != '':
        year = past_time.split(' ')[3]
        small_time = past_time.split(' ')[4]
    else:
        year = past_time.split(' ')[4]
        small_time = past_time.split(' ')[5]
    day = past_time.split(' ')[1]
    month = past_time.split(' ')[2]
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
    return year + '-' + month + '-' + day +  ' ' + small_time + ':00'

#author 陈宣齐
class Detiknews(BaseSpider):
    name = 'detiknews'
    website_id =  16 # 网站的id(必填)
    language_id =  1952 # 所用语言的id
    # allowed_domains = ['inside.kompas.com']
    start_urls = ['https://news.detik.com/indeks']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        past_time = time.time() - 86400
        url_time = time.strftime("%d-%m-%Y", time.localtime(time.time()))
        for i in soup.select('nav.static-nav.sticky > ul.nav.nav--column > li'):
            yield Request(url=i.find('a').get('href') + '?date=' + url_time, meta={'category1':i.text.strip('\n'),'past_time':past_time},callback=self.parse_2)

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        img = ''
        if page_soup.find('div', class_='grid-row list-content') is not None:
            for i in page_soup.select('div.grid-row.list-content > article'):
                title = i.find('h3', class_='media__title').text.strip('\n').strip('                        ')
                if i.find('div', class_='media__text').find('a').get('href') == '#':
                    news_url = i.get('i-link')
                else:
                    news_url = i.find('div', class_='media__text').find('a').get('href')
                if i.find('img') is not None:
                    img = i.find('img').get('src')
                else:
                    img = i.get('i-img')
                yield Request(url=news_url, meta={'title':title, 'img':img, 'category1':response.meta['category1']},callback=self.parse_3)
        elif page_soup.find('section', class_='list__news no-img') is not None:
            for i in page_soup.select('section.list__news.no-img > article'):
                news_url = i.find('a').get('href')
                title = i.find('h3').text.strip('\n')
                yield Request(url=news_url, meta={'title':title, 'img':img, 'category1':response.meta['category1']},callback=self.parse_3)
        elif page_soup.find('ul', class_='list feed') is not None:
            for i in page_soup.select('ul.list.feed > li'):
                news_url = i.find('a').get('href')
                title = i.find('a').text.strip('\n')
                yield Request(url=news_url, meta={'title':title, 'img':img, 'category1':response.meta['category1']},callback=self.parse_3)
        elif page_soup.find('ul', class_='list') is not None:
            for i in page_soup.select('ul.list > li'):
                news_url = i.find('a').get('href')
                title = i.find('a').text.strip('\n')
                yield Request(url=news_url, meta={'title':title, 'img':img, 'category1':response.meta['category1']},callback=self.parse_3)
        elif page_soup.find('ul', class_='list_feed list_indeks') is not None:
            for i in page_soup.select('ul.list_feed list_indeks > li'):
                news_url = i.find('a').get('href')
                title = i.find('a').text.strip('\n')
                yield Request(url=news_url, meta={'title':title, 'img':img, 'category1':response.meta['category1']},callback=self.parse_3)

        if page_soup.find('div', class_='pagination text-center mgt-16 mgb-16') is not None:
            if page_soup.select('div.pagination.text-center.mgt-16.mgb-16 > a')[-1].get('href') is not None:
                yield Request(url=page_soup.select('div.pagination.text-center.mgt-16.mgb-16 > a')[-1].get('href'), meta={'category1':response.meta['category1'],'past_time':response.meta['past_time']},callback=self.parse_2)
            else:
                return
        elif page_soup.find('div', class_='pagination') is not None:
            if page_soup.select('div.pagination > a')[-1].get('href') != response.url:
                yield Request(url=page_soup.select('div.pagination > a')[-1].get('href'), meta={'category1':response.meta['category1'],'past_time':response.meta['past_time']},callback=self.parse_2)
            else:
                return
        elif page_soup.find('div', class_='pagination-indeks') is not None:
            if page_soup.select('div.pagination-indeks > a')[-1].get('href') != response.url:
                yield Request(url=page_soup.select('div.pagination-indeks > a')[-1].get('href'), meta={'category1':response.meta['category1'],'past_time':response.meta['past_time']},callback=self.parse_2)
            else:
                return
        elif page_soup.find('ul', class_='paging') is not None:
            if page_soup.select('ul.paging > li > a')[-1].get('href') != response.url:
                yield Request(url=page_soup.select('ul.paging > li > a')[-1].get('href'), meta={'category1':response.meta['category1'],'past_time':response.meta['past_time']},callback=self.parse_2)
            else:
                return

        last_day = int(response.meta['past_time'])
        if self.time == None or int(last_day) >= int(self.time):  # 截止功能
            last_url_time = time.strftime("%d-%m-%Y", time.localtime(last_day))
            last_url = response.url.split('?')[0] + '?date=' + last_url_time
            last_day = int(response.meta['past_time']) - 86400
            yield Request(url=last_url,meta={'category1':response.meta['category1'],'past_time':last_day},callback=self.parse_2)
        else:
            self.logger.info("时间截至")


    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text, 'lxml')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['body'] = ''
        if new_soup.find('div', class_='itp_bodycontent read__content pull-left') is not None:
            for i in new_soup.find('div', class_='itp_bodycontent read__content pull-left').find_all('p'):
                item['body'] += i.text
        elif new_soup.find('div', class_='detail__body-text itp_bodycontent') is not None:
            for i in new_soup.find('div', class_='detail__body-text itp_bodycontent').find_all('p'):
                item['body'] += i.text
        elif new_soup.find('div', class_='itp_bodycontent detail__body-text') is not None:
            for i in new_soup.find('div', class_='itp_bodycontent detail__body-text').find_all('p'):
                item['body'] += i.text
        elif new_soup.find('div', class_='itp_bodycontent detail_text') is not None:
            for i in new_soup.find('div', class_='itp_bodycontent detail_text').find_all('p'):
                item['body'] += i.text
        if item['body'] != '':
            item['abstract'] = item['body'].split('.')[0]
        if new_soup.find('div', class_='read__photo') is not None:
            item['images'] = [new_soup.find('div', class_='read__photo').find('img').get('src')]
        if new_soup.find('div', class_='media_artikel wide') is not None:
            if new_soup.find('div', class_='media_artikel wide').find('img') is not None:
                item['images'] = [new_soup.find('div', class_='media_artikel wide').find('img').get('src')]
        else:
            item['images'] = [response.meta['img']]
        if new_soup.find('span', class_='date') is not None:
            item['pub_time'] = time_font_2(new_soup.find('span', class_='date').text)
        elif new_soup.find('div', class_='detail__date') is not None:
            item['pub_time'] = time_font_2(new_soup.find('div', class_='detail__date').text)
        elif new_soup.find('div', class_='date') is not None:
            item['pub_time'] = time_font_2(new_soup.find('div', class_='date').text)
        if item['body'] != '':
            yield item
