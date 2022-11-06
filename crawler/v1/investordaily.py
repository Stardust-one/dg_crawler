from crawler.spiders import BaseSpider
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
    day = past_time.split(' ')[0]
    month = past_time.split(' ')[1]
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
class investordaily(BaseSpider):
    name = 'investordaily'
    website_id = 5 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://www.investordaily.com.au/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.find('ul', class_='b-bqe').find_all('li')[:-1]:
            yield Request(url='https://www.investordaily.com.au' + i.find('a').get('href'),callback=self.parse_2)

    def parse_2(self, response, **kwargs):
        page_soup = BeautifulSoup(response.text, 'lxml')
        last_url = ''
        if page_soup.find('ul', class_='b-bey') is not None:
            for i in page_soup.find('ul', class_='b-bey').find_all('li', class_='b_dis'):
                if i.find('a') is not None:
                    news_url = i.find('a').get('href')
                    last_url = news_url
                    if i.find('a', class_='b-ogi') is not None:
                        title = i.find('a', class_='b-ogi').text.strip('\n').strip(
                            '                                    ')
                    else:
                        title = i.find('a').text.strip('\n').strip('                                    ')
                    if i.find('p', class_='b-mrs') is not None:
                        abstract = i.find('p', class_='b-mrs').text.strip('\n').strip(
                            '                                        ')
                    else:
                        abstract = i.find('a').text.strip('\n').strip('                       ')
                    imgs = []
                    if i.find('img') is not None:
                        if i.find('img').get('data-src') is not None:
                            imgs = ['https://www.investordaily.com.au' + i.find('img').get('data-src')]
                        elif i.find('img').get('src') != '/images/basic/icon-right-arrow.svg':
                            imgs = ['https://www.investordaily.com.au' + i.find('img').get('src')]
                    yield Request('https://www.investordaily.com.au' + news_url,callback=self.parse_3,meta={'img':imgs,'title':title,'abstract':abstract})
            if last_url != '':
                last_page = BeautifulSoup(
                    requests.get('https://www.investordaily.com.au' + last_url).text, 'lxml')
                if last_page.find('time', class_='b-dzq') is not None:
                    last_time = time_font_5(
                        last_page.find('time', class_='b-dzq').text.strip('\n').strip('            '))
                    if page_soup.find('ul', class_='pagination') is not None:
                        next_page = 'https://www.investordaily.com.au/' + \
                              page_soup.find('ul', class_='pagination').find_all('li')[-2].find('a').get('href')
                        if self.time == None or Util.format_time3(last_time) >= int(self.time):
                            yield Request(url=next_page,callback=self.parse_2)
                        else:
                            self.logger.info("时间截止")

    def parse_3(self,response):
        new_soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['title'] = response.meta['title']
        item['images'] = response.meta['img']
        item['abstract'] = response.meta['abstract']
        item['category1'] = new_soup.find_all('span', itemprop='name')[0].text
        item['category2'] = new_soup.find_all('span', itemprop='name')[1].text
        item['body'] = ''
        if new_soup.find('time', class_='b-dzq') is not None:
            item['pub_time'] = time_font_5(new_soup.find('time', class_='b-dzq').text.strip('\n').strip('            '))
            for i in new_soup.find('div', class_='b_xvb').find_all('p'):
                item['body'] += i.text
        yield item