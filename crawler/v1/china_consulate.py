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
class china_consulateSpider(BaseSpider):
    name = 'china_consulate'
    website_id = 382 # 网站的id(必填)
    language_id = 1813  # 所用语言的id
    start_urls = ['http://medan.china-consulate.org/chn/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
         
        

    glo_index = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")

        category_hrefList = []
        # category_nameList = []
        categories = soup.select("div.nbox_r.fr a") if soup.select("div.nbox_r.fr a") else None
        for category in categories:
            category_hrefList.append("http://medan.china-consulate.org/chn/" + category.get('href')[2:])
            # category_nameList.append(category.text)

        for category in category_hrefList:
            yield scrapy.Request(category, callback=self.parse_category)

    def parse_category(self, response, index=glo_index):
        soup = BeautifulSoup(response.text, features="lxml")
        flag = True

        if self.time is None or Util.format_time3(re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", soup.select("div.nbox_ul a")[-1].text).group() + " 00:00:00") >= int(self.time):
            article_hrefs = []
            articles = soup.select("div.nbox_ul a") if soup.select("div.nbox_ul a") else None
            if articles:
                for article in articles:
                    article_hrefs.append(re.search("^.*/", response.url).group() + article.get("href")[2:])
            for detail_url in article_hrefs:
                yield Request(detail_url, callback=self.parse_detail)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag and index < int(re.search(r"countPage = [0-9]*", str(soup.select_one("div#pages script"))).group().strip()[12:]):
            next_page = re.search("^.*/", response.url).group() + "default_" + str(index) + ".htm"
            global glo_index
            glo_index = index + 1
            yield Request(next_page, callback=self.parse_category)
        # else:
        #     index = 1
        #     if self.time is None or Util.format_time3(soup.select("ul[style=\"margin-left:5px\"] li span")[-1].text.replace("(", "").replace(")", "") + " 00:00:00") >= int(self.time):
        #         next_page = re.search("^.*/", response.url).group() + "default_" + str(index) + ".htm"
        #         index = index + 1
        #         meta = {"index": index}
        #         yield Request(next_page, callback=self.parse_category, meta=meta)





    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        pub_time = soup.select_one("div#News_Body_Time").text.replace("/", "-") if soup.select_one("div#News_Body_Time") else None
        item['pub_time'] = pub_time + " 00:00:00"
        image_list = []
        imgs = soup.find("table", class_="myaddedit FCK__ShowTableBorders").select('td img') if soup.find("table", class_="myaddedit FCK__ShowTableBorders") else None
        if imgs:
            for img in imgs:
                image_list.append(re.search("^.*/", response.url).group() + img.get("oldsrc"))
        item['images'] = image_list

        p_list = []
        if soup.select("div.News_Body_Text p"):
            all_p = soup.select("div.News_Body_Text p")
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
            item['body'] = body
            item['abstract'] = p_list[0]

        item['category1'] = soup.select("div.Top_Index_A a")[-1].text if soup.select("div.Top_Index_A a") else None
        # item['category2'] = soup.select("ul.td-category li")[1].text if soup.select("ul.td-category li") and len(soup.select("ul.td-category li")) >= 2 else None
        item['title'] = soup.select_one("div#News_Body_Title").text if soup.select_one("div#News_Body_Title") else None
        yield item



def time_adjustment(input_time):
    time_elements = input_time.split(" ")
    date = time_elements[0].split("-")

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


    return "%s-%s-%s %s" % (date[2], date[1], date[0], time_elements[1])
