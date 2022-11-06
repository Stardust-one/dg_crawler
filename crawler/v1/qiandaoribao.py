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

def time_font_5(past_time):
    #March 22, 2021
    day = past_time.split(' ')[1].strip(',')
    month = past_time.split(' ')[0]
    year = past_time.split(' ')[2]
    if month == 'January':
        month = '01'
    elif month == 'February':
        month = '02'
    elif month == 'March':
        month = '03'
    elif month == 'April':
        month = '04'
    elif month == 'May':
        month = '05'
    elif month == 'June':
        month = '06'
    elif month == 'July':
        month = '07'
    elif month == 'August':
        month = '08'
    elif month == 'September':
        month = '09'
    elif month == 'October':
        month = '10'
    elif month == 'November':
        month = '11'
    else:
        month = '12'
    return year + '-' + month + '-' + day + ' 00:00:00'

#author 陈宣齐
class QiandaoribaoSpider(BaseSpider):
    name = 'qiandaoribao'
    website_id = 12  # 网站的id(必填)
    language_id = 1813  # 所用语言的id
    allowed_domains = ['qiandaoribao.com']
    start_urls = ['http://qiandaoribao.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.find('div', class_='jeg_nav_item jeg_mainmenu_wrap').find('ul',class_='jeg_menu jeg_main_menu jeg_menu_style_5').find_all('li')[1:]:
            yield Request(url=i.find('a').get('href'),callback=self.parse_2,meta={'category1':i.find('a').text})

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        img = ''
        abstart = ''
        last_time = ''
        if page_soup.find('div', class_='jeg_posts jeg_load_more_flag') is not None:
            for i in page_soup.find('div', class_='jeg_posts jeg_load_more_flag').find_all('article'):
                if i.find('img') is not None:
                    img = i.find('img').get('data-src')
                url = i.find('a').get('href')
                title = i.find('h3', class_='jeg_post_title').text.strip('\n')
                pub_time = time_font_5(i.find('div', class_='jeg_meta_date').text.strip('\n').strip(' '))
                last_time = pub_time
                if i.find('div', class_='jeg_post_excerpt') is not None:
                    abstart = i.find('div', class_='jeg_post_excerpt').text.strip('\n')
                yield Request(url=url,callback=self.parse_3,meta={'title':title,'img':img,'pub_time':pub_time,'abstart':abstart,'category1':response.meta['category1']})
        if page_soup.find('div',class_='jeg_navigation jeg_pagination jeg_pagenav_1 jeg_aligncenter no_navtext no_pageinfo') is not None:
            if self.time == None or Util.format_time3(last_time) >= int(self.time):
                next_page = page_soup.find('div',class_='jeg_navigation jeg_pagination jeg_pagenav_1 jeg_aligncenter no_navtext no_pageinfo').find('a',class_='page_nav next').get('href')
                yield Request(url=next_page,callback=self.parse_2,meta={'category1':response.meta['category1']})
            else:
                self.logger.info("时间截止")

    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text, 'lxml')
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['body'] = ''
        for i in new_soup.find('div', class_='content-inner').find_all('p'):
            item['body'] += i.text
        if response.meta['abstart'] == '':
            item['abstract'] = item['body'].split('。')[0]
        else:
            item['abstract'] = response.meta['abstart']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item