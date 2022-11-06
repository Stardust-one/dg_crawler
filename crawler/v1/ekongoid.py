from crawler.spiders import BaseSpider
import scrapy
from crawler.items import *
from utils.util_old import *
from bs4 import BeautifulSoup as bs
import re

#author 郭贤玉
class ekongoidSpider(BaseSpider):
    name = 'ekongoid'
    website_id =  80 # 网站的id(必填)
    language_id = 1952  # 所用语言的id

    allowed_domains = ['ekon.go.id']#一点开就变成这个网址
    start_urls = ['https://www.ekon.go.id']

    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
         
        

    def parse(self, response):
        '''
        :param response:
        :return:二级目录链接
        '''

        soup = bs(response.text, "html.parser")

        item = NewsItem()
        Pro = soup.select_one("#navbarNav > ul > li:nth-child(3)")
        for ur in Pro.select("a")[1:-3]:
            category1_url = self.start_urls[0] + ur.get("href")
            item['category1'] = Pro.select_one("a").text.strip()
            # print(category1)
            yield scrapy.Request(category1_url, meta={"item": item},callback=self.get_next_page)  # 层与层之间通过meta参数传递数据
        Info = soup.select_one("#navbarNav > ul > li:nth-child(7)")
        for ur in Info.select("a")[1:]:
            category1_url = self.start_urls[0]  + ur.get("href")
            item['category1'] = Info.select_one("a").text.strip()


            yield scrapy.Request(category1_url, meta={"item": item},callback=self.get_next_page)  # 层与层之间通过meta参数传递数据
    def get_next_page(self, response):
            soup = bs(response.text, "html.parser")
            item = response.meta['item']

            category1_2 = soup.find("div", class_="row border-bottom m-0")

            item['category2'] = category2 = category1_2.select_one("a").text

            article_div = soup.find_all("div", class_="col-md-8")
            for div in article_div:
                article_url = self.start_urls[0] + div.select_one("a").get("href")
                yield scrapy.Request(article_url, callback=self.get_news_detail, meta={"item": item})  # 层与层之间通过meta参数传递数据

            last_time = re.split('WIB| ', article_div[-1].select_one("span").text)
            temp_time = last_time[1] + ' ' + last_time[0] + ' ' + last_time[2] + ' ' + last_time[3]

            if self.time == None or Util.format_time3(Util.format_time2(temp_time)) >= int(self.time):
                li = soup.find_all("li", class_="page-item")[-1]
                if li.select_one("a"):
                    next_url = li.select_one("a").get("href")
                    yield scrapy.Request(next_url, meta={"item": item}, callback=self.get_next_page)
            else:
                    self.logger.info('时间截止')

    def get_news_detail(self,response):
        '''
        :param response: x新闻正文response
        :return: 新闻页面详情信息
        '''
        item = response.meta["item"]

        soup = bs(response.text, "html.parser")

        title = soup.select_one("h4").text

        last_time = re.split('WIB| ', soup.find("div", class_="row m-2").select_one("span").text)
        pub_time = Util.format_time2(last_time[1] + ' ' + last_time[0] + ' ' + last_time[2] + ' ' + last_time[3])

        div = soup.find("div", class_="row md-m-5 m-2")
        image_list = [i.get("src") for i in div.select("img")]

        body = ''
        body_p = soup.select("#print > div:nth-child(3) > div.text-justify.mt-3 > p") if soup.select("#print > div:nth-child(3) > div.text-justify.mt-3 > p") else soup.select("#print > div:nth-child(3) > div > p")
        for p in body_p:
            body += (p.text.strip() + '\n')

        abstract = body.split(".")[0]

        item["pub_time"] =  pub_time
        item["images"] = image_list
        item["abstract"] = abstract
        item["body"] = body
        item["title"] = title.strip()

        yield item


