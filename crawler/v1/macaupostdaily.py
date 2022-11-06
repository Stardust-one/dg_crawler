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

#author 陈宣齐
class macaupostdaily(BaseSpider):
    name = 'macaupostdaily'
    website_id = 674 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://www.macaupostdaily.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    # 这是类初始化函数，用来传时间戳参数
    
          
        


    def parse(self, response, **kwargs):
        news_soup = BeautifulSoup(response.text,'lxml')
        last_time = ''
        for i in news_soup.find('ul', class_='new_list', id='fu').find_all('li'):
            news_url = 'https://www.macaupostdaily.com/' + i.find('a').get('href')
            title = i.find('div', class_='text').find('a').text
            abstract = i.find('p').text
            pub_time = i.find('div', class_='time').text.strip('\n').strip(' ') + ':00'
            last_time = pub_time
            img = 'https://www.macaupostdaily.com/' + i.find('img').get('src')
            yield Request(url=news_url,callback=self.parse_2,meta={'time':pub_time,'title':title,'abstract':abstract,'img':img})

        if self.time == None or Util.format_time3(last_time) >= int(self.time):
            page = 2
            Data = {
                'cid': '',
                'page': '%d' % page
            }
            post_url = 'https://www.macaupostdaily.com/index.php/Article/news_list'
            yield scrapy.FormRequest(url=post_url,formdata=Data,callback=self.parse_post,meta={'page':page})
        else:
            print("超时啦!!")

    def parse_post(self,response):
        rep = json.loads(response.text)
        last_time = ''
        for i in rep['list']:
            news_url = 'https://www.macaupostdaily.com//article' + i['id'] + '.html'
            title = i['title']
            img = 'https://www.macaupostdaily.com/' + i['img']
            pub_time = i['time'] + ':00'
            last_time = pub_time
            abstract = i['content']
            yield Request(url=news_url,callback=self.parse_2,meta={'time':pub_time,'title':title,'abstract':abstract,'img':img})
        if self.time == None or Util.format_time3(last_time) >= int(self.time):
            post_url = 'https://www.macaupostdaily.com/index.php/Article/news_list'
            page = response.meta['page'] + 1
            Data = {
                'cid': '',
                'page': '%d' % page
            }
            yield scrapy.FormRequest(url=post_url, formdata=Data, callback=self.parse_post,meta={'page':page})
        else:
            print("超时啦!!")

    def parse_2(self,response):
        new_soup = BeautifulSoup(response.text , 'lxml')
        item = NewsItem()
        item['pub_time'] = response.meta['time']
        item['title'] = response.meta['title']
        item['images'] = response.meta['img']
        item['abstract'] = response.meta['abstract']
        item['body'] = ''
        for i in new_soup.find('div', class_='art_cont').find_all('p'):
            item['body'] += i.text.strip('\n').strip(' ')
        item['category1'] = ''
        item['category2'] = ''
        yield item

