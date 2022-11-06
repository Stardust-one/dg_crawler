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

# author: 陈宝胜
def dailyexpress_time_switch1(time_string):
    # July 05, 2021
    # 返回时间戳
    return Util.format_time3(str(datetime.strptime(time_string, "%B %d, %Y")))

def dailyexpress_time_switch2(time_string):
    # July 16, 2003
    # 返回标准时间
    return datetime.strptime(time_string, "%B %d, %Y")

# 将爬虫类名和name字段改成对应的网站名
class DailyexpressSpider(BaseSpider):
    name = 'dailyexpress'
    website_id = 152  # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ["http://www.dailyexpress.com.my/local/?location='Keningau'",
                  "http://www.dailyexpress.com.my/local/?location='Kota Belud'",
                  "http://www.dailyexpress.com.my/local/?location='Kota Kinabalu'",
                  "http://www.dailyexpress.com.my/local/?location='Labuan'",
                  "http://www.dailyexpress.com.my/local/?location='Lahad Datu'",
                  "http://www.dailyexpress.com.my/local/?location='Papar'",
                  "http://www.dailyexpress.com.my/local/?location='Ranau'",
                  "http://www.dailyexpress.com.my/local/?location='Sandakan'",
                  "http://www.dailyexpress.com.my/local/?location='Tawau'",
                  "http://www.dailyexpress.com.my/local/?location='Tenom'",
                  "http://www.dailyexpress.com.my/local/?location='Tuaran'",
                  "http://www.dailyexpress.com.my/sarawak/",
                  "http://www.dailyexpress.com.my/west-malaysia",
                  "http://www.dailyexpress.com.my/asean/"
                  "http://www.dailyexpress.com.my/world/",
                  "http://www.dailyexpress.com.my/business/",
                  "http://www.dailyexpress.com.my/sports/",
                  "http://www.dailyexpress.com.my/hotline/",
                  "http://www.dailyexpress.com.my/sabah-in-history/",
                  "http://www.dailyexpress.com.my/special/",
                  "http://www.dailyexpress.com.my/opinions/",
                  "http://www.dailyexpress.com.my/forum/",
                  "http://www.dailyexpress.com.my/property/",
                  "http://www.dailyexpress.com.my/auto/",
                  "http://www.dailyexpress.com.my/education/",
                  "http://www.dailyexpress.com.my/food/",
                  "http://www.dailyexpress.com.my/health/",
                  "http://www.dailyexpress.com.my/tech/",
                  "http://www.dailyexpress.com.my/travel/",
                  "http://www.dailyexpress.com.my/branded",
                  "http://www.dailyexpress.com.my/harian/"
                  ]
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          

    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        for news_url in ["http://www.dailyexpress.com.my" + a.get("href") for a in soup.select(".container .row .col-lg-8.col-md-8.col-sm-12.col-xs-12 table .title a")[:-6]]:
            yield scrapy.Request(news_url, callback=self.parse_detail)
        next_page = "http://www.dailyexpress.com.my/" + soup.select_one(".container .row .col-lg-8.col-md-8.col-sm-12.col-xs-12 > a").get("href") if soup.select_one(".news")is None else None
        LastTimeStamp = dailyexpress_time_switch1(soup.select(".container .row .col-lg-8.col-md-8.col-sm-12.col-xs-12 table .content")[-6].find("div", style="font-size:12px; color:#999;").text.strip().split("\n")[0]) if soup.select(".container .row .col-lg-8.col-md-8.col-sm-12.col-xs-12 table .content") else None
        if self.time is None or LastTimeStamp >= self.time:
            if next_page:
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                self.logger.info("该目录已经到底")
        else:
            self.logger.info("时间截止")

    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        item['title'] = soup.select_one(".title.titlemobile ").text
        item['pub_time'] = dailyexpress_time_switch2(soup.find("div", style='font-size:12px; color:#999;').text.split(", ", 1)[1])
        item['category1'] = soup.select_one(".crumb.hideprint .tagLabel a").text if soup.select_one(".crumb.hideprint .tagLabel a") else None
        item['category2'] = None
        item['images'] = ["http://www.dailyexpress.com.my" + img.get("src") for img in soup.select(".imgcaptiondiv img")] if soup.select(".imgcaptiondiv img") else []
        item['body'] = soup.select_one("#newsContent .newsContent").text.strip().replace("ADVERTISEMENT\n", "") if soup.select_one("#newsContent .newsContent") else ""
        item['abstract'] = item['body'].split("\n")[0] if item['body'] is not None else None
        item['website_id'] = self.website_id
        item['language_id'] = self.language_id
        item['request_url'] = response.request.url
        item['response_url'] = response.url
        item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        yield item
