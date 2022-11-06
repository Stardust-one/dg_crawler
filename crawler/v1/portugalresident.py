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
class portugalresidentSpider(BaseSpider):
    name = 'portugalresident'
    website_id = 689 # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ['https://www.portugalresident.com/']
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
        categories = soup.select("ul#menu-main-menu-1 li a") if soup.select("ul#menu-main-menu-1 li a") else None
        del categories[-1], categories[-1], categories[1]
        for category in categories:
            if category.get('href') == "/cinema-listings":
                complete = "https://www.portugalresident.com/category/entertainment" + category.get('href')
                category_hrefList.append(complete)
            else:
                category_hrefList.append(category.get('href'))
            # category_nameList.append(category.text)

        for category in category_hrefList:
            yield scrapy.Request(category, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        flag = True
        last_time = [etime.text for etime in soup.find_all("time", class_="entry-date updated td-module-date")]
        if self.time is None or Util.format_time3(time_adjustment(last_time[-4])) >= int(self.time):
            article_hrefs = []
            if soup.select("div.td-module-meta-info a"):
                articles = soup.select("div.td-module-meta-info a")
                for a in articles:
                    if a.text == "Read more" or a.text == soup.select_one("span.td-bred-no-url-last").text:
                        articles.remove(a)
                for article in articles:
                    article_hrefs.append(article.get('href'))
            else:
                articles = soup.find_all("h3", class_="entry-title td-module-title")
                for a in articles:
                    article_hrefs.append(a.select_one("a").get('href'))

            for detail_url in article_hrefs:
                yield Request(detail_url, callback=self.parse_detail)
            else:
                self.logger.info("到达最后一页")

        else:
            flag = False
            self.logger.info("时间截止")

        if flag and soup.find("div", class_="page-nav td-pb-padding-side"):
            next_page_href = soup.find("div", class_="page-nav td-pb-padding-side").select("a")[-1].get('href')
            yield scrapy.Request(next_page_href, callback=self.parse_category)


    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')

        item['pub_time'] = time_adjustment(soup.find("time", class_="entry-date updated td-module-date").text)
        image_list = []
        if soup.select_one("div.td-post-featured-image a"):
            image_list.append(soup.select_one("div.td-post-featured-image a").get("href"))
        if soup.find("div", class_="td-post-content tagdiv-type").select("p img"):
            for img in soup.find("div", class_="td-post-content tagdiv-type").select("p img"):
                image_list.append(img.get("data-lazy-src"))
        item['images'] = image_list

        p_list = []
        if soup.find("div", class_="td-post-content tagdiv-type"):
            all_p = soup.find("div", class_="td-post-content tagdiv-type").select("p")
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
            item['body'] = body
            item['abstract'] = all_p[0].text

        item['category1'] = soup.select("ul.td-category li")[0].text
        item['category2'] = soup.select("ul.td-category li")[1].text if soup.select("ul.td-category li") and len(soup.select("ul.td-category li")) >= 2 else None
        item['title'] = soup.select_one("h1.entry-title").text if soup.select_one("h1.entry-title").text else None
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


    return "%s-%s-%s %s" % (time_elements[2], month[time_elements[1]], day, "00:00:00")
