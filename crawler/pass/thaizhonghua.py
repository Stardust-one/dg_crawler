import scrapy
from utils.date_util import DateUtil
from crawler.items import NewsItem
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from common.header import UA_LIST
import requests
import json
import socket
import re
import time
from datetime import datetime

# author : 詹婕妤
from crawler.spiders import BaseSpider


class ThaizhonghuaSpider(BaseSpider):
    name = 'thaizhonghua'
    allowed_domains = ['thaizhonghua.com']
    start_urls = ['https://thaizhonghua.com/']
    website_id = 225  # 网站的id(必填)
    language_id = 1813  # 所用语言的id
    # proxy = '01'

    post_url = 'https://thaizhonghua.com/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=10.3'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
    }

    data = {
        'action': 'td_ajax_loop',
        'loopState[sidebarPosition]':'',
        'loopState[moduleId]': '10',
        'loopState[currentPage]': '1',
        'loopState[max_num_pages]': '21',
        'loopState[atts][category_id]': '17',
        'loopState[atts][offset]': '4',
        'loopState[ajax_pagination_infinite_stop]': '3',
        'loopState[server_reply_html_data]':''
    }

    def parse(self,response):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(response.text,'html.parser')
        for i in soup.select('#menu-td-demo-header-menu > li')[1:-2]:
            category1 = i.find('a').text
            for a in i.select('ul .menu-item-0'):
                category2 = a.find('a').text
                url = a.find('a').get('href')
                yield Request(url,callback=self.parse2 ,meta={'category1':category1,'category2':category2})

    def parse2(self,response):
        flag1 = True
        flag2 = True
        if response.url != self.post_url:
            soup = BeautifulSoup(response.text,'html.parser')
            response.meta['max_num_pages'] = re.findall(r'loopState.max_num_pages = \d+',response.text)[-1].split()[-1]
            response.meta['currentPage'] = '1'
            response.meta['category_id'] = re.findall(r"'category_id':\d+", response.text)[0].split(':')[-1]
            # self.logger.info(response.meta['category_id'])
            response.meta['moduleId'] = re.findall(r'loopState.moduleId = \S+',response.text)[0].split("'")[1]


            # self.logger.info(soup.select('.td_block_inner .td-meta-align'))
            for i in soup.select('.td_block_inner .td-meta-align'):
                url = i.select_one('.entry-title.td-module-title a').get('href')
                response.meta['title'] = i.select_one('.entry-title.td-module-title a').text
                response.meta['pub_time'] = time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(url.split('/')[3]),int(url.split('/')[4]),int(url.split('/')[5])).timetuple())
                if self.time == None or DateUtil.formate_time2time_stamp(response.meta['pub_time']) >= int(self.time):
                    yield Request(url, callback=self.parse_item, meta=response.meta)
                else:
                    flag1 = False
                    self.logger.info('时间截止')
                if flag1 is False:
                    break

        else:
            soup = BeautifulSoup(json.loads(response.text)['server_reply_html_data'],'html.parser')
            url_list = []
            if soup.select('.item-details') != []:
                url_list = soup.select('.item-details')
            elif soup.select('.td-block-span6') != []:
                url_list = soup.select('.td-block-span6')
            if url_list != []:
                for i in url_list:
                    response.meta['title'] = i.select_one('.entry-title.td-module-title a').text
                    article_url = i.select_one('.entry-title.td-module-title a').get('href')
                    response.meta['pub_time'] = time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(article_url.split('/')[3]), int(article_url.split('/')[4]),int(article_url.split('/')[5])).timetuple())
                    if self.time == None or DateUtil.formate_time2time_stamp(response.meta['pub_time']) >= int(self.time):
                        yield Request(article_url,callback=self.parse_item,meta=response.meta)
                    else:
                        flag2 = False
                        self.logger.info('时间截止')
                    if flag2 is False:
                        break


        if flag2:
            self.data['loopState[max_num_pages]'] = response.meta['max_num_pages']
            self.data['loopState[moduleId]'] = response.meta['moduleId']
            self.data['loopState[category_id]'] = response.meta['category_id']
            if int(response.meta['currentPage']) <= int(response.meta['max_num_pages']):
                self.logger.info(self.data['loopState[currentPage]'])
                self.data['loopState[currentPage]'] = response.meta['currentPage']
                response.meta['currentPage'] = str(int(response.meta['currentPage']) + 1)
                yield scrapy.FormRequest(self.post_url ,callback=self.parse2 ,meta=response.meta ,method='POST' ,formdata=self.data)



    def parse_item(self,response):
        item = NewsItem()
        soup = BeautifulSoup(response.text,'html.parser')
        body = ''
        for p in soup.select('.td-post-content.tagdiv-type p'):
            body += p.text + '\n'
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        item['images'] = [img.get('src') for img in soup.select('.td-post-content.tagdiv-type img')]if soup.select('.td-post-content.tagdiv-type img') else []
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        yield item



