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
class kemenagSpider(BaseSpider):
    name = 'kemenag'
    website_id = 101 # 网站的id(必填)
    language_id = 1952  # 所用语言的id
    start_urls = ['https://www.kemenag.go.id/']
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
        categories = soup.select("div.main_menu div.menu-primary-container.navigation_wrapper ul#mainmenu li > a")
        del categories[0], categories[-1], categories[-1], categories[-1], categories[-1]
        for category in categories:
            category_hrefList.append("https://www.kemenag.go.id" + category.get('href'))
            # category_nameList.append(category.text)
        category_hrefList.remove("https://www.kemenag.go.id/topik")
        category_hrefList.remove("https://www.kemenag.go.idinformasi")
        category_hrefList.remove("https://www.kemenag.go.idlayanan")
        category_hrefList.remove("https://www.kemenag.go.idhttps://ppid.kemenag.go.id/v4/if_berkala.php")
        category_hrefList.remove("https://www.kemenag.go.idhttps://ppid.kemenag.go.id/v4/if_tersedia.php")
        for category in category_hrefList:
            yield scrapy.Request(category, callback=self.parse_category)



    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        if soup.select_one("div.col-md-6.mb-4"):
            flag = True
            pub_time = time_adjustment(re.search("[0-9]* .* [0-9]{4}$", soup.select("div.col-md-6.mb-4 span.post-date")[-1].text).group().strip()) if soup.select("div.col-md-6.mb-4 span.post-date") else None
            if self.time is None or Util.format_time3(pub_time) >= int(self.time):
                article_hrefs = []
                articles = soup.select("div.row div.col-md-6.mb-4 h3.entry-title a")
                if articles:
                    for article in articles:
                        article_hrefs.append("https://www.kemenag.go.id" + article.get("href"))
                for detail_url in article_hrefs:
                    yield Request(detail_url, callback=self.parse_detail)
            else:
                flag = False
                self.logger.info("时间截止")

            if flag and soup.select_one("a.next.page-numbers"):
                yield Request(soup.select_one("a.next.page-numbers").get("href"), callback=self.parse_category)
        else:
            self.logger.info("无资讯页")

    def parse_detail(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text, features='lxml')
        item['pub_time'] = time_adjustment(re.search("[0-9]* .* .*:[0-9]{2}", soup.select_one("li.entry__meta-date").text.strip()).group().strip()) if soup.select_one("li.entry__meta-date") else None
        image_list = []
        imgs = soup.select("div.image-post-thumb.jlsingle-title-above img")
        if imgs:
            for img in imgs:
                image_list.append(img.get("src"))
        item['images'] = image_list

        content_list = []
        if soup.select("div.post_content.jl_content p"):
            content = soup.select("div.post_content.jl_content p")
            for paragraph in content:
                content_list.append(paragraph.text)
            body = '\n'.join(content_list)
            item['body'] = body
            item['abstract'] = content_list[0]

        item['category1'] = soup.select("div.single_post_entry_content.single_bellow_left_align.jl_top_single_title.jl_top_title_feature span.meta-category-small.single_meta_category")[2].text.strip() if soup.select("div.single_post_entry_content.single_bellow_left_align.jl_top_single_title.jl_top_title_feature span.meta-category-small.single_meta_category") else None
        # item['category2'] = soup.select("div.jeg_meta_category a")[1].text if len(soup.select("div.jeg_meta_category a")) >= 2 else None
        item['title'] = soup.select_one("h1.single_post_title_main").text if soup.select_one("h1.single_post_title_main") else None
        yield item


def time_adjustment(input_time):
    time_elements = input_time.split(" ")
    if int(time_elements[0]) < 10:
        time_elements[0] = "0" + time_elements[0]

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
    # month = {
    #     'January': '01',
    #     'February': '02',
    #     'March': '03',
    #     'April': '04',
    #     'May': '05',
    #     'June': '06',
    #     'July': '07',
    #     'August': '08',
    #     'September': '09',
    #     'October': '10',
    #     'November': '11',
    #     'December': '12'
    # }
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
    # month = {       # 印尼语缩写
    #     'Jan': '01',
    #     'Feb': '02',
    #     'Mar': '03',
    #     'Apr': '04',
    #     'Mei': '05',
    #     'Jun': '06',
    #     'Jul': '07',
    #     'Agu': '08',
    #     'Sep': '09',
    #     'Okt': '10',
    #     'Nov': '11',
    #     'Des': '12'
    # }
    month = {       # 印尼语
        'Januari': '01',
        'Februari': '02',
        'Maret': '03',
        'April': '04',
        'Mei': '05',
        'Juni': '06',
        'Juli': '07',
        'Agustus': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12'
    }

    if len(time_elements) == 3:
        return "%s-%s-%s %s" % (time_elements[2], month[time_elements[1]], time_elements[0], " 00:00:00")
    else:
        return "%s-%s-%s %s" % (time_elements[2], month[time_elements[1]], time_elements[0], time_elements[3] + ":00")