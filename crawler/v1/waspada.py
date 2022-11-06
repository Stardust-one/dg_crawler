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
class waspadaSpider(BaseSpider):
    name = 'waspada'
    website_id = 135 # 网站的id(必填)
    language_id = 1952  # 所用语言的id
    start_urls = ['https://waspada.co.id/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
         
        


    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")

        category_hrefList = list(set([i.get("href") for i in soup.select("div.jeg_nav_item.jeg_mainmenu_wrap li a") if i.get("href") != "#"]))
        category_hrefList.remove("https://jabar.waspada.co.id/")
        category_hrefList.remove("https://waspada.co.id/")
        category_hrefList.remove("https://waspada.co.id/warta-terkini/")
        # category_nameList = []
        # categories = soup.find("div", class_="container main-menu dropdown-menu fullwidth navbar-collapse collapse").select("ul > li.dropdown.mega-full.menu-color > a") if soup.find("div", class_="container main-menu dropdown-menu fullwidth navbar-collapse collapse") else None
        # for category in categories:
        #     category_hrefList.append(category.get('href'))
            # category_nameList.append(category.text)

        for category in category_hrefList:
            yield scrapy.Request(category, callback=self.parse_category)


    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        flag = True
        pub_time = time_adjustment(re.search("[0-9]{4}.*$", soup.select("div.jeg_inner_content div.jeg_meta_date a")[-1].text).group()) if soup.select("div.jeg_inner_content div.jeg_meta_date a") else None
        if self.time is None or Util.format_time3(pub_time) >= int(self.time):
            article_hrefs = []
            articles = soup.select("div.jeg_inner_content h3.jeg_post_title a") if soup.select("div.jeg_inner_content h3.jeg_post_title a") else None
            if articles:
                for article in articles:
                    article_hrefs.append(article.get("href"))
            for detail_url in article_hrefs:
                yield Request(detail_url, callback=self.parse_detail)
        else:
            flag = False
            self.logger.info("时间截止")

        if soup.select("div.jeg_navigation.jeg_pagination.jeg_pagenav_1.jeg_aligncenter.no_navtext.no_pageinfo a"):
            if flag and soup.select("div.jeg_navigation.jeg_pagination.jeg_pagenav_1.jeg_aligncenter.no_navtext.no_pageinfo a")[-1].text == "Next":
                yield Request(soup.select("div.jeg_navigation.jeg_pagination.jeg_pagenav_1.jeg_aligncenter.no_navtext.no_pageinfo a")[-1].get("href"), callback=self.parse_category)


    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        item['pub_time'] = re.search("[0-9]{4}.*$", soup.select_one("div.jeg_meta_date").text).group().replace("/", "-").strip() + ":00" if soup.select_one("div.jeg_meta_date") else None
        # image_list = []
        # imgs =
        # if imgs:
        #     for img in imgs:
        #         image_list.append(img.get("src"))
        item['images'] = [soup.select_one("div.jeg_inner_content div.thumbnail-container.animate-lazy > img").get("data-src")] if soup.select_one("div.jeg_inner_content div.thumbnail-container.animate-lazy > img") else None

        p_list = []
        if soup.select("div.entry-content.no-share div.content-inner p"):
            all_p = soup.select("div.entry-content.no-share div.content-inner p")
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
            item['body'] = body
            item['abstract'] = p_list[0]

        item['category1'] = soup.select("div.jeg_meta_category a")[0].text if soup.select("div.jeg_meta_category a") else None
        item['category2'] = soup.select("div.jeg_meta_category a")[1].text if len(soup.select("div.jeg_meta_category a")) >= 2 else None
        item['title'] = soup.select_one("h1.jeg_post_title").text if soup.select_one("h1.jeg_post_title") else None
        yield item


def time_adjustment(input_time):
    # time_elements = input_time.split(" ")
    # day = re.sub('th$|st$|nd$|rd$', '', time_elements[0])
    # if int(day) < 10:
    #     day = "0" + day

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


    # return "%s-%s-%s %s" % (time_elements[2], month[time_elements[1]], day, " 00:00:00")
    return input_time.replace("/", "-").strip() + ":00"
