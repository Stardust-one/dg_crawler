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

# author: 陈宝胜 -2021/7/15
# 将爬虫类名和name字段改成对应的网站名
class BorneopostSpider(BaseSpider):
    name = 'borneopost'
    website_id = 155  # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ['https://www.theborneopost.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for category_url in [a.get("href") for a in soup.select("#menu-main-menu > li > a")[1:]]:
            yield scrapy.Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for news_url in [a.get("href") for a in soup.select(".row .posts-list.listing-alt article .post-wrap > a")]:
            yield scrapy.Request(news_url, callback=self.parse_detail)
        LastTimeStamp = Util.format_time3(
            soup.select(".row .posts-list.listing-alt article .content time")[-1].get("datetime").split("+")[0].replace(
                "T", " "))
        next_page = soup.select_one(".next.page-numbers").get("href") if soup.select_one(".next.page-numbers") else None
        if self.time is None or LastTimeStamp >= int(self.time):
            if next_page is not None:
                yield scrapy.Request(next_page, callback=self.parse_category)
            else:
                self.logger.info("目录已经到底")
        else:
            self.logger.info("时间截止")

    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        breadcrumbs = soup.select(".breadcrumbs > span")
        item['category1'] = breadcrumbs[3].text
        item['category2'] = breadcrumbs[5].text if len(breadcrumbs) == 8 else None
        item['title'] = soup.select_one(".heading.cf h1").text.strip()
        item['pub_time'] = soup.select_one(".post-meta.cf .dtreviewed time").get("datetime").split("+")[0].replace("T", " ")
        item['body'] = "\n".join([p.text for p in soup.select(".post-content.description > p")])
        item['abstract'] = item['body'].split("\n", 1)[0]
        item['images'] = [img.get("src") for img in soup.select(".post-content.description div img")]
        item['website_id'] = self.website_id
        item['language_id'] = self.language_id
        item['request_url'] = response.request.url
        item['response_url'] = response.url
        item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        yield item