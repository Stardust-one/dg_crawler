from crawler.spiders import BaseSpider
# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from datetime import datetime
import time
import re

def intimes_time_switch1(time_string):
    # 06 07, 2021
    # 返回时间戳
    return Util.format_time3(str(datetime.strptime(time_string, "%d %m, %Y")))

def intime_time_switch2(time_string):
    # 2021-07-06T11:05:37+08:00
    # 返回格式时间
    return time_string.split("+")[0].replace("T", " ")

# author 陈宝胜
class IntimesSpider(BaseSpider):
    name = 'intimes'
    website_id = 141  # 网站的id(必填)
    language_id = 2266  # 所用语言的id
    start_urls = ['http://intimes.com.my/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for category in [a.get("href") for a in soup.select("#gkTopNav nav#gkExtraMenu li a")[2:8]]:
            yield scrapy.Request("http://intimes.com.my"+category, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for news_url in [a.get("href") for a in soup.select(".itemList header h2 a")]:
            yield scrapy.Request("http://intimes.com.my"+news_url, callback=self.parse_detail)
        next_page = "http://intimes.com.my" + soup.select_one(".pagination-next a").get("href") if soup.select_one(".pagination-next a").get("href") else None
        LastTimeStamp = intimes_time_switch1(soup.select(".itemBlock time")[-1].text)
        if self.time is None or LastTimeStamp >= self.time:
            if next_page is not None:
                scrapy.Request(next_page, callback=self.parse_category)
            else:
                self.logger.info("该目录已经到底")
        else:
            self.logger.info("时间截止")

    def parse_detail(self, response):
        self.logger.info(response.url + "进入parse_detail!!!!!!!!!!!!!!!!!!!!")
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        item['title'] = soup.select_one("#k2Container h1").text
        item['images'] = [a.get("href") for a in soup.select(".itemBodyWrap .itemImageBlock a")] if soup.select(".itemBodyWrap .itemImageBlock a") else []
        item['abstract'] = soup.select_one(".itemIntroText").text if soup.select_one(".itemIntroText").text else ""
        item['body'] = item['abstract'].join([p.text for p in soup.select(".itemFullText p")])
        item['category1'] = soup.select_one("header ul li a").text
        item['category2'] = None
        item['pub_time'] = intime_time_switch2(soup.select_one("header li time").get("datetime"))
        item['website_id'] = self.website_id
        item['language_id'] = self.language_id
        item['request_url'] = response.request.url
        item['response_url'] = response.url
        item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        yield item

