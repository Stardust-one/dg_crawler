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
    #Mon, June 7, 2021
    month = past_time.split(' ')[1]
    day = past_time.split(' ')[2].strip(',')
    year = past_time.split(' ')[-1]
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

class thejakartapost(BaseSpider):
    name = 'thejakartapost'
    website_id = 3 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['http://www.thejakartapost.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        news_soup = BeautifulSoup(response.text, 'lxml')
        for i in news_soup.find('ul',class_='tjp-ul-6').find_all('a')[1:]:
            yield Request(url=i.get('href'),callback=self.parse_2)
        yield Request(url=news_soup.find('li',class_='tjp-li-9-0').find('a').get('href'),callback=self.parse_2)

    def parse_2(self,response):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36 Edg/80.0.361.61'
        }
        last_time = ''
        page = BeautifulSoup(response.text, 'lxml')
        if page.find('div', class_='theLatest mb-20') is not None:
            for i in page.find('div', class_='theLatest mb-20').find_all('div', class_='listNews columns'):
                news_url = 'https://www.thejakartapost.com/' + i.find('div', class_='imageLatest').find('a').get('href')
                news_img = i.find('div', class_='imageLatest').find('img').get('data-src')
                title = i.find('h2', class_='titleNews').text.strip('\n').strip(
                    '                                            ').strip('\n')
                category1 = i.find('span', class_='dt-news').text
                yield Request(url=news_url,callback=self.parse_3,meta={'title':title,'news_img':news_img,'category1':category1})
            last_time = time_font_3(BeautifulSoup(requests.get(url='https://www.thejakartapost.com/' + page.find('div', class_='theLatest mb-20').find_all('div', class_='listNews columns')[-1].find('div', class_='imageLatest').find('a').get('href'),headers=header).text \
                                              ,'lxml').find('span',class_='posting').find('span',class_='day').text)
        elif page.find('div', class_='col-xs-12 columns bgSingle mainNews') is not None:
            for i in page.find('div', class_='col-xs-12 columns bgSingle mainNews').find_all('div',
                                                                                             class_='listNews whtPD columns'):
                news_url = i.find('div', class_='imageNews').find('a').get('href')
                news_img = i.find('div', class_='imageNews').find('img').get('data-src')
                title = i.find('h2', class_='titleNews').text.strip('\n').strip(
                    '                                            ').strip('\n')
                if i.find('span', class_='dt-news') is not None:
                    category1 = i.find('span', class_='dt-news').text
                elif i.find('span', class_='dt-se-asia') is not None:
                    category1 = i.find('span', class_='dt-se-asia').text
                elif i.find('span', class_='dt-opinion') is not None:
                    category1 = i.find('span', class_='dt-opinion').text
                else:
                    category1 = ''
                last_time = time_font_3(BeautifulSoup(requests.get(page.find('div', class_='col-xs-12 columns bgSingle mainNews').find_all('div',
                                    class_='listNews whtPD columns')[-1].find('div', class_='imageNews').find('a').get('href'),headers=header).text,'lxml').find('span',class_='posting').find('span',class_='day').text)
                yield Request(url=news_url,callback=self.parse_3,meta={'title':title,'news_img':news_img,'category1':category1})
        elif page.find('ul', id='tjp-control-paging') is not None:
            for i in page.find_all('ul', id='tjp-control-paging'):
                for a in i.find_all('li'):
                    if a.find('div', class_='image-latest') is not None:
                        if a.find('div', class_='image-latest').find('a').get('href')[0] != 'h':
                            news_url = 'https://www.thejakartapost.com' + a.find('div', class_='image-latest').find(
                                'a').get('href')
                            news_img = a.find('div', class_='image-latest').find('img').get('data-src')
                            title = a.find('div', class_='detail-latest').find('h5').text.strip('\n').strip(
                                '                                            ').strip('\n')
                            if i.find('span', class_='dt-news') is not None:
                                category1 = i.find('span', class_='dt-news').text
                            elif i.find('span', class_='dt-opinion') is not None:
                                category1 = i.find('span', class_='dt-opinion').text
                            elif i.find('span', class_='dateSite') is not None:
                                category1 = \
                                i.find('span', class_='dateSite').text.split('                                 ')[
                                    0].strip('\n').strip('                                 ').strip('\n')
                            else:
                                category1 = ''
                            yield Request(url=news_url,callback=self.parse_3,meta={'title':title,'news_img':news_img,'category1':category1})
                            # print("需要进去才能那abstract")
                        else:
                            news_url = a.find('div', class_='image-latest').find('a').get('href')
                            news_img = a.find('div', class_='image-latest').find('img').get('data-src')
                            title = a.find('div', class_='detail-latest').find('h5').text.strip('\n').strip(
                                '                                            ').strip('\n')
                            if i.find('span', class_='dt-news') is not None:
                                category1 = i.find('span', class_='dt-news').text
                            elif i.find('span', class_='dt-opinion') is not None:
                                category1 = i.find('span', class_='dt-opinion').text
                            elif i.find('span', class_='dateSite') is not None:
                                category1 = \
                                i.find('span', class_='dateSite').text.split('                                 ')[
                                    0].strip('\n').strip('                                 ').strip('\n')
                            else:
                                category1 = ''
                            yield Request(url=news_url,callback=self.parse_3,meta={'title':title,'news_img':news_img,'category1':category1})
        if page.find('div', class_='navigation-page') is not None:
            next_page = 'https://www.thejakartapost.com/' + page.find('div', class_='navigation-page').find_all('a')[-1].get(
                'href')
            if last_time != '':
                if self.time == None or Util.format_time3(last_time) >= int(self.time):
                    yield Request(next_page,callback=self.parse_2)
        elif page.find('div', class_='columns tjp-newsPagination') is not None:
            next_page = response.request.url.split('?')[0] + page.find('div', class_='columns tjp-newsPagination').find('a').get('href')
            if last_time != '':
                if self.time == None or Util.format_time3(last_time) >= int(self.time):
                    yield Request(next_page,callback=self.parse_2)

    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text,'lxml')
        item['title'] = response.meta['title']
        item['images'] = response.meta['news_img']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['body'] = ''
        item['abstract'] = ''
        if new_soup.find('span', class_='created') is not None:
            item['abstract'] = new_soup.find('span', class_='created').text.strip('\n').strip(
                '                              ').strip('\n')
        elif new_soup.find('p', class_='created') is not None:
            item['abstract'] = new_soup.find('p', class_='created').text.strip('\n').strip(
                '                              ').strip('\n')
        if new_soup.find('div', class_='col-md-10 col-xs-12 detailNews') is not None:
            for i in new_soup.find('div', class_='col-md-10 col-xs-12 detailNews').find_all('p'):
                item['body'] += i.text.strip('\n')
        elif new_soup.find('div', class_='show-define-text') is not None:
            for i in new_soup.find('div', class_='show-define-text').find_all('p'):
                item['body'] += i.text.strip('\n')
        if new_soup.find('span',class_='posting').find('span',class_='day') is not None:
            item['pub_time'] = time_font_3(new_soup.find('span',class_='posting').find('span',class_='day').text)
        if item['body'] != '' and item['pub_time'] != '':
            yield item
