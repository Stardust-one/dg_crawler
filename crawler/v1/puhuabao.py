from crawler.spiders import BaseSpider
from datetime import datetime
import scrapy
from crawler.items import *
from bs4 import BeautifulSoup as bs
from utils.util_old import *
import time
import re

#author 郭贤玉
class PuhuabaoSpider(BaseSpider):
    name = 'puhuabao'
    website_id= 686
    language_id = 1813
    # allowed_domains = ['puhuabao.pt']
    start_urls = ['http://www.puhuabao.pt']
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    sql = {  # sql配置
            'host': '192.168.235.162',#新的
            'user': 'dg_admin',#'wsh'
            'password': 'dg_admin',
            'db': 'dg_crawler'
        }
    
         
        

    def parse(self, response):
        item = NewsItem()
        soup = bs(response.text, 'html.parser')

        a_list = soup.select("body>div>div>div>div>div>div>div>ul>li>a")
        for a in a_list[1:-1]:
            item['category1'] = a.text.strip()
            category_url = a.get("href")
            # print(category1 + '\t' + category_url)

            yield scrapy.Request(category_url, callback=self.parse_category, meta={"item": item})

    def parse_category(self, response):
        soup = bs(response.text, 'html.parser')
        item = response.meta["item"]

        div_list = soup.find_all("div", class_="td-read-more")
        for div in div_list:
            news_url = div.select_one("a").get("href")
            yield scrapy.Request(news_url, callback=self.parse_detail, meta={"item": item})

        temp_time = soup.find("div", class_="td-ss-main-content").find_all("span", class_="td-post-date")[-1].text.strip() if soup.find("div", class_="td-ss-main-content") else None
        new_temp_time = ''
        for t in re.split('年|月|日', temp_time):
            new_temp_time = new_temp_time + t + ' '
        data = time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(re.split('年|月|日', temp_time)[0]), int(re.split('年|月|日', temp_time)[1]),int(re.split('年|月|日', temp_time)[2]), 0, 0).timetuple())

        if self.time == None or Util.format_time3(data) >= int(self.time):
            a = soup.find("div", class_="page-nav td-pb-padding-side").select("a")[-1]
            if a.select_one("i") != None:
                url = a.get("href")
                yield scrapy.Request(url, callback=self.parse_category, meta={"item": item})
        else:
            self.logger.info('时间截止')

    def parse_detail(self, response):
        item = response.meta["item"]
        soup = bs(response.text,'html.parser')

        title = soup.find("h1", class_="entry-title").text.strip() if soup.find("h1", class_="entry-title") else None
        # print("title" + '\t' + title)

        temp_time = soup.find("div", class_="td-module-meta-info").select_one("time").text  # 时间的字符串
        pub_time = time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(re.split('年|月|日', temp_time)[0]), int(re.split('年|月|日', temp_time)[1]), int(re.split('年|月|日', temp_time)[2]), 0, 0).timetuple())
        # print("pub_time" + '\t' + pub_time)
        img_list = []
        if soup.find("div", class_="td-post-featured-image"):
            img_list.append(soup.find("div", class_="td-post-featured-image").select_one("a").get("href"))
        # print(img_list)
        body_div = soup.find("div", class_="td-post-content")
        abstract = body_div.select("p")[0].text if body_div.select("p") else None
        # print("abstract:" + '\t' + abstract)

        body = ''

        for s in body_div.select("section"):
            body += (s.text.strip() + '\n')
            if s.select("img"):
                img_list.append(s.select_one("img").get("src"))  # 文章中间的图片

        for p in body_div.select("p"):
            body += (p.text.strip() + '\n')
            if p.select("img"):
                img_list.append(p.select_one("img").get("src"))  # 文章中间的图片
        item['category2'] = ''
        item["title"] = title
        item["pub_time"] = pub_time
        item["images"] = img_list
        item["abstract"] = abstract
        item["body"] = body
        yield item

