from crawler.spiders import BaseSpider
import json

import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup


# author 刘鼎谦
class MmgpmediaSpider(BaseSpider):
    name = 'mmgpmedia'
    # allowed_domains = ['www.mmgpmedia.com']
    start_urls = [
                  'http://www.mmgpmedia.com/web/RD/index.html',
                  'http://www.mmgpmedia.com/web/YW/index.html',
                  'http://www.mmgpmedia.com/web/CJ/index.html',
                  'http://www.mmgpmedia.com/web/ZH/index.html',
                  'http://www.mmgpmedia.com/web/MH/index.html',
                  'http://www.mmgpmedia.com/web/SX/index.html',
                  'http://www.mmgpmedia.com/web/HQ/index.html',
                  'http://www.mmgpmedia.com/web/WNL/index.html',
                  'http://www.mmgpmedia.com/web/SJ/index.html',
                  'http://www.mmgpmedia.com/web/MFN/index.html'
                  ]

    website_id = 1451  # 网站的id(必填)
    language_id = 1813  # 双语语言 中文:1813 缅甸语:2065  (MFN栏目下，新闻少)
    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'local_crawler',
    #     'password': 'local_crawler',
    #     'db': 'local_dg_test'
    # }
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    getAPI = 'http://cms.offshoremedia.net/front/list/latest?pageNum={}&pageSize=10&siteId=752495108259188736&channelId={}'

    # 每个一级标题下面有pageNum pageSize ChannelID 、siteID相同

    
          
        

    def parse(self, response):  # 拿必要参数
        channelId = re.findall("var channelId = '\d+", response.text)[0].replace("var channelId = '", '')
        # pageSize = re.findall("var pageSize = \d+", response.text)[0].replace('var pageSize = ', '')    # 都是10
        pageNum = '1'  # 初始都为1
        url = self.getAPI.format(pageNum, channelId)
        return Request(url=url, callback=self.parse_page)

    def parse_page(self, response):  # 翻页、拿新闻、时间截止
        js = json.loads(response.text)
        last_pub_time = int(js['info']['list'][-1]['contentPublishTime'] / 1000)  # last_pub_time 再js中直接就是时间戳
        flag = True
        if self.time is None or last_pub_time >= int(self.time):
            for i in js['info']['list']:
                meta = {
                    'category1': i['contentChannelName'],
                    'pub_time_stamp': i['contentPublishTime'] / 1000,
                    'title': i['contentTitle'],
                    'abstract': i['contentAbstract'],
                }
                if '752841778121678848' == i['contentChannelId']:  # 缅甸语一级标题下的id
                    meta['language_id'] = 2065
                else:
                    meta['language_id'] = 1813
                yield Request(url=i['contentStaticPage'], callback=self.parse_item, meta=meta)
        else:
            self.logger.info("时间截止")
            flag = False
        if flag:
            currentPage = re.findall('pageNum=\d+', response.url)[0].replace('pageNum=', '')
            if int(currentPage) < js['info']['pages']:
                nextPage = str(int(currentPage) + 1)
                url = self.getAPI.format(nextPage, js['info']['list'][0]['contentChannelId'])
                self.logger.info(nextPage)
                self.logger.info(url)
                yield Request(url=url, callback=self.parse_page)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('.article_content img')]
        item['pub_time'] = self.timeStamp2String(response.meta['pub_time_stamp'])
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('.article_content p')])
        item['abstract'] = response.meta['abstract']
        return item

    @classmethod
    def timeStamp2String(self, timeStamp):
        timeArray = time.localtime(timeStamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
