from crawler.spiders import BaseSpider
# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
from datetime import datetime
import time

# author: 陈宝胜
def therocket_time_switch1(time_string):
    # June 27, 2021
    # 返回时间戳
    return Util.format_time3(str(datetime.strptime(time_string, "%B %d, %Y")))


def therocket_time_switch2(time_string):
    # June 27, 2021
    # 返回标准时间
    return str(datetime.strptime(time_string, "%B %d, %Y"))


class TherocketSpider(BaseSpider):
    name = 'therocket'
    website_id = 140  # 网站的id(必填)
    language_id = 2266  # 所用语言的id
    start_urls = ['https://therocket.com.my/cn/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        category_list = [a.get("href") for a in soup.select_one("#td-header-menu").select("div #menu-td-demo-footer"
                                                                                          "-menu-1 li a")]
        for url in category_list:
            if re.match("https://therocket.com.my/cn/category/", url):
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        category1 = soup.select(".entry-crumbs span")[-1].text
        Last_pubtime = ''
        for details in soup.select(".td-ss-main-content .item-details"):
            item = NewsItem()
            body_list = [d.text for d in details.select(".td-excerpt")]
            pub_time = details.select_one(".td-module-meta-info time").text
            item['body'] = "\n".join(body_list)
            item['abstract'] = body_list[0]
            item['pub_time'] = therocket_time_switch2(pub_time)
            item['title'] = details.select_one("h3 a").text
            item['request_url'] = details.select_one("h3 a").get("href")
            item['response_url'] = item['request_url']
            item['website_id'] = self.website_id
            item['language_id'] = self.language_id
            item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            item['category1'] = category1
            item['category2'] = None
            item['images'] = details.parent.select_one(".td-module-thumb img").get("src")
            Last_pubtime = pub_time
            yield item
        next_num = int(soup.select_one(".page-nav.td-pb-padding-side .current").text) + 1 if soup.select_one(
            ".page-nav.td-pb-padding-side .current") else None
        last_num = int(soup.select_one(".td-pb-row span.pages").text.rsplit(" ", 1)[-1]) if soup.select_one(
            ".td-pb-row span.pages") else None
        LastTimeStamp = therocket_time_switch1(Last_pubtime)
        if self.time is None or LastTimeStamp >= self.time:
            if next_num is not None and last_num is not None and next_num <= last_num:
                url = response.url.split("/page")[0]
                yield scrapy.Request(url + '/page/' + str(next_num), callback=self.parse_category)
            else:
                self.logger.info("目录已经到底")
        else:
            self.logger.info("时间截止")

    # def parse_detail(self, response):
    #     soup = BeautifulSoup(response.text, features="lxml")
    #     if soup.select_one(".td-404-title"):  # 判断页面
    #         self.logger.info("该界面404!")
    #         return
    #     else:
    #         item = NewsItem()
    #         body_list = [b.text for b in soup.find_all("div", dir="auto")] if soup.find_all("div", dir="auto") else [
    #             p.text for p in soup.find_all("p", dir="auto")] if soup.find_all("p", dir="auto") else None
    #         if body_list is None:
    #             return
    #         else:
    #             item['body'] = "\n".join(body_list)
    #             item['title'] = soup.select_one("header.td-post-title h1").text
    #             item['images'] = [a.get("href") for a in soup.select(".td-post-featured-image a")] if soup.select(
    #                 ".td-post-featured-image a") else []
    #             item['abstract'] = body_list[0] if body_list is not None else None
    #             item['pub_time'] = therocket_time_switch2(soup.select_one(".td-post-date").text)
    #             item['website_id'] = self.website_id
    #             item['language_id'] = self.language_id
    #             item['request_url'] = response.request.url
    #             item['response_url'] = response.url
    #             item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    #             item['category1'] = soup.select_one(".entry-category").text
    #             item['category2'] = None
    #             yield item
