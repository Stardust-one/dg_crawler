from crawler.spiders import BaseSpider

# 此文件包含的头文件不要修改
import requests
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
from datetime import datetime

#将爬虫类名和name字段改成对应的网站名
# author：梁海麟
class antaranewsSpider(BaseSpider):
    name = 'antaranews'
    website_id = 371 # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ['https://en.antaranews.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
         
        


    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")

        category_hrefList = []
        # category_nameList = []
        categories = soup.find("div", class_="container main-menu dropdown-menu fullwidth navbar-collapse collapse").select("ul > li.dropdown.mega-full.menu-color > a") if soup.find("div", class_="container main-menu dropdown-menu fullwidth navbar-collapse collapse") else None
        for category in categories:
            category_hrefList.append(category.get('href'))
            # category_nameList.append(category.text)

        for category in category_hrefList:
            yield scrapy.Request(category, callback=self.parse_category)


    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        flag = True
        pub_time = Util.format_time2(soup.select("div.col-md-8 article span")[-1].text.strip()) if re.search(".*ago$", soup.select("div.col-md-8 article span")[-1].text.strip()) else time_adjustment(soup.select("div.col-md-8 article span")[-1].text.strip())
        if self.time is None or Util.format_time3(pub_time) >= int(self.time):
            article_hrefs = []
            articles = soup.select("article.simple-post.simple-big.clearfix > header > h3 > a") if soup.select("article.simple-post.simple-big.clearfix > header > h3 > a") else None
            if articles:
                for article in articles:
                    article_hrefs.append(article.get("href"))
            for detail_url in article_hrefs:
                category = soup.select_one("h3.block-title").text
                yield Request(detail_url, callback=self.parse_detail, meta={"category1": category})
        else:
            flag = False
            self.logger.info("时间截止")

        if flag and soup.select("ul.pagination.pagination-sm li")[-1].text == "»":
            yield Request(soup.select("ul.pagination.pagination-sm li")[-1].select_one("a").get("href"), callback=self.parse_category)


    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        item['pub_time'] = Util.format_time2(soup.select_one("header.post-header.clearfix > p.simple-share > span.article-date").text.strip()) if re.search(".*ago$", soup.select_one("header.post-header.clearfix > p.simple-share > span.article-date").text.strip()) else time_adjustment(soup.select_one("header.post-header.clearfix > p.simple-share > span.article-date").text.strip())
        image_list = []
        imgs = soup.select("header.post-header.clearfix img")
        if imgs:
            for img in imgs:
                image_list.append(img.get("src"))
        item['images'] = image_list

        p_list = []
        if soup.select("div.post-content.clearfix"):
            all_p = soup.select("div.post-content.clearfix")
            for paragraph in all_p:
                p_list.append(paragraph.text.strip())
            body = '\n'.join(p_list)
            item['body'] = body
            item['abstract'] = p_list[0]

        item['category1'] = response.meta["category1"]
        # item['category2'] = soup.select("ul.td-category li")[1].text if soup.select("ul.td-category li") and len(soup.select("ul.td-category li")) >= 2 else None
        item['title'] = soup.select_one("h1.post-title").text if soup.select_one("h1.post-title") else None
        yield item


def time_adjustment(input_time):
    time_elements = input_time.split(" ")
    day = re.sub('th$|st$|nd$|rd$', '', time_elements[0])
    if int(day) < 10:
        day = "0" + day

    # month = {     # 印地语
    #     'जनवरी': '01',
    #     'फ़रवरी': '02',
    #     'जुलूस': '03',
    #     'अप्रैल': '04',
    #     'मई': '05',
    #     'जून': '06',
    #     'जुलाई': '07',
    #     'अगस्त': '08',
    #     'सितंबर': '09',
    #     'अक्टूबर': '10',
    #     'नवंबर': '11',
    #     'दिसंबर': '12'
    # }
    month = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }
    # month = {       # 葡萄牙语
    #     'janeiro': '01',
    #     'fevereiro': '02',
    #     'março': '03',
    #     'abril': '04',
    #     'maio': '05',
    #     'junho': '06',
    #     'julho': '07',
    #     'agosto': '08',
    #     'setembro': '09',
    #     'outubro': '10',
    #     'novembro': '11',
    #     'dezembro': '12'
    # }
    # month = {
    #     'Jan': '01',
    #     'Feb': '02',
    #     'Mar': '03',
    #     'Apr': '04',
    #     'May': '05',
    #     'Jun': '06',
    #     'Jul': '07',
    #     'Aug': '08',
    #     'Sep': '09',
    #     'Oct': '10',
    #     'Nov': '11',
    #     'Dec': '12'
    # }


    return "%s-%s-%s %s" % (time_elements[2], month[time_elements[1]], day, " 00:00:00")
