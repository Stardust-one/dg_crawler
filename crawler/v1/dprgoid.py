from crawler.spiders import BaseSpider
import scrapy
from crawler.items import *
from bs4 import BeautifulSoup as bs
from utils.util_old import *
import time
from datetime import datetime

def translate(m):
    '''
        翻译印尼语的月份
    '''
    if  m=='Desember':
        m = "12"
    if  m=='Nopember':
        m = "11"
    if  m=='Oktober':
        m = "10"
    if m == 'September':
        m = "9"
    if m == 'Agustus':
        m = "8"
    if m == 'Juli':
        m = "7"
    if m == 'Juni':
        m = "6"
    if m == 'Mei':
        m = "5"
    if m == 'April':
        m = "4"
    if m ==  'Maret':
        m = "3"
    if m == 'Februari':
        m = "2"
    if m ==  'Januari':
        m = "1"
    return m

#author郭贤玉
class dprSpider(BaseSpider):
    name = 'dprgoid'
    website_id =  75 # 网站的id(必填)
    language_id = 1952  # 所用语言的id

    allowed_domains = ['dpr.go.id']
    start_urls = ['https://www.dpr.go.id/berita',]
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    page_num = 0
    max_page = 0
    home_url = "https://www.dpr.go.id"

    def parse(self, response):
        '''

        :param response:
        :return: 最大页码数
        '''
        soup = bs(response.text, "html.parser")

        page_div = soup.find("div", class_="col-md-2 col-xs-3 text-right")
        self.max_page = int(page_div.select("a")[-1].get("href").split("/")[-1]) if page_div.select("a")[-1] else 0
        yield scrapy.Request(response.url,callback=self.parse_get_next_page)

    def parse_get_next_page(self, response):
        '''
        :param response:
        :return:一级目录链接
        '''
        # item = NewsItem()

        soup = bs(response.text, "html.parser")

        body_div = soup.find_all("div", class_="col-md-50 col-xs-50 berita-item")
        for article in body_div:
            article_url = article.select_one("a").get("href")

            yield scrapy.Request("https://www.dpr.go.id"+article_url,meta=response.meta,callback=self.get_news_detail)

        temp_time = body_div[-1].select("div")[-3].text.split("/")[0].strip() if body_div[-1].select("div")[-3].text.split("/")[0].strip() else None
        time_list = temp_time.split(" ")
        #06 Juli 2021 /
        last_time = time_list[2]+"-"+translate(time_list[1])+"-"+time_list[0]+ ' 00:00:00'
        # self.logger.info("----------------------------------------------------------------------------")
        # self.logger.info(last_time)

        if self.time == None or Util.format_time3(last_time) >= int(self.time):

                self.page_num += 1
                if self.page_num<=self.max_page:

                    next_url = self.start_urls[0]+"/index/hal/"+str(self.page_num)
                    yield scrapy.Request(next_url, meta=response.meta, callback=self.parse_get_next_page)
        else:
            self.logger.info('时间截止')

    def get_news_detail(self,response):
        '''
        :param response: x新闻正文response
        :return: 新闻页面详情信息
        '''
        item = NewsItem()
        soup = bs(response.text,"html.parser")

        image_list = []
        div = soup.find("div", class_="col-md-9 col-md-offset-2")
        img = div.select("img")
        # print(img)
        for i in img:
            image_list.append("https://www.dpr.go.id" + i.get("src"))

        title = soup.find("h3", class_="text-center").text.strip()

        pub_time_list = soup.select_one("#detail > div > div > div.col-md-9.col-md-offset-2 > div.date.text-center.mb25").text.split( "/")[0].strip().split("-")

        pub_time = time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(pub_time_list[2]), int(pub_time_list[1]), int(pub_time_list[0])).timetuple())

        category2 = soup.select_one("#detail > div > div > div.col-md-9.col-md-offset-2 > div.date.text-center.mb25>span").text.strip()

        abstract = soup.select_one(
            "#detail > div > div > div.col-md-9.col-md-offset-2 > div.content.mb30 > h5").text if soup.select_one(
            "#detail > div > div > div.col-md-9.col-md-offset-2 > div.content.mb30 > h5") else None

        if abstract == None:
            abstract = soup.select("#detail > div > div > div.col-md-9.col-md-offset-2 > div.content.mb30 > p")[2].text
        body = ''
        # print(soup.select("#detail > div > div > div.col-md-9.col-md-offset-2 > div.content.mb30 > p"))
        for p in soup.select("#detail > div > div > div.col-md-9.col-md-offset-2 > div.content.mb30 > p"):
            if p.text != " ":
                body += (p.text + '\n')

        item["category1"] = "BERITA"
        item["category2"] = category2
        item["title"] = title
        item["pub_time"] = pub_time
        item["images"] = image_list
        item["abstract"] = abstract
        item["body"] = body
        yield item