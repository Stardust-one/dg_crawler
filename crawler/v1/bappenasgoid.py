from crawler.spiders import BaseSpider
import scrapy
from crawler.items import *
from utils.util_old import *
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
import re

def new_format_time2(s):
    '''

    :param s:原时间格式为Aug 19th, 2010 10:33 am
    :return: 返回2020-11-24 9:42:00
    '''
    pub_time = re.split(" |,|:|-|th|st|nd|rd", s.strip())
    #防止八月的单词被切割
    if pub_time[0]=='Augu':
        pub_time[0] = 'August'
    # print(pub_time)
    #文章里的时间切割完之后变这样['Aug', '19', '', '', '2010', '10', '33', 'am']
    # 翻页那里的时间切割王之后变成这样['October', '12', '', '2020']
    month = pub_time[0]
    month = month.strip()
    if month == "Jan":
        month = 1
    elif month == "Feb":
        month = 2
    elif month == "Mar":
        month = 3
    elif month == "Apr":
        month = 4
    elif month == "May":
        month = 5
    elif month == "Jun":
        month = 6
    elif month == "Jul":
        month = 7
    elif month == "Aug":
        month = 8
    elif month == "Sep":
        month = 9
    elif month == "Sept":
        month = 9
    elif month == "Oct":
        month = 10
    elif month == "Nov":
        month = 11
    elif month == "Dec":
        month = 12
    elif month == "January":
        month = 1
    elif month == "February":
        month = 2
    elif month == "March":
        month = 3
    elif month == "April":
        month = 4
    elif month == "May":
        month = 5
    elif month == "June":
        month = 6
    elif month == "July":
        month = 7
    elif month == "August":
        month = 8
    elif month == "September":
        month = 9
    elif month == "October":
        month = 10
    elif month == "November":
        month = 11
    elif month == "December":
        month = 12
    pub_time = [i for i in pub_time if i != '']
    # if len(pub_time)>4:
    year = pub_time[2]
    day = pub_time[1]
    hour = pub_time[-3] if pub_time[-1] == 'am' else int(pub_time[-3]) + 12
    if hour == 24:
            hour = 12
    minute = pub_time[-2]

    return time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(year), month, int(day), int(hour), int(minute)).timetuple())

#author 郭贤玉
class bappenasgoidSpider(BaseSpider):
    name = 'bappenasgoid'
    website_id =  77 # 网站的id(必填)
    language_id = 1952  # 所用语言的id

    allowed_domains = ['bappenas.go.id']#一点开就变成这个网址
    start_urls = ['https://www.bappenas.go.id']

    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    page_num = -10
    max_page = 0


    def parse(self, response):
        '''
        :param response:
        :return:二级目录链接
        '''

        soup = bs(response.text, "html.parser")
        item = NewsItem()
        item['category1'] = soup.select_one("#bp-main-menu > div.bg-a.grid-container.vert-center.bp-header-container > div.grid-60.mobile-grid-100.grid-parent.bp-main-menu.hor-inline.text-center > div:nth-child(4) > h3 > a").text

        li_list = soup.select(
            "#bp-main-menu > div.grid-100.accent-blue-solid.bp-submenu-container.text-white > div > ul:nth-child(4) > li")
        for li in li_list[:-1]:
            category1_url = self.start_urls[0]+li.select_one("a").get("href")
            # item['category2'] = li.select_one("a").text
            yield scrapy.Request(category1_url, callback=self.get_next_page,meta={"item":item})  # 层与层之间通过meta参数传递数据


    def get_next_page(self, response):
            soup = bs(response.text, "html.parser")
            item = response.meta["item"]

            article_div = soup.find_all("div", class_="grid-100 grid-parent entry margin-bottom-15px")

            for article in article_div:
                article_url = self.start_urls[0] + article.select_one("div>h2>a").get("href")

                yield scrapy.Request(article_url, callback=self.get_news_detail, meta={"item": item})  # 层与层之间通过meta参数传递数据

            temp_time = article_div[-1].select_one("div>h4").text.strip()

            if self.time == None or Util.format_time3(Util.format_time2(temp_time)) >= int(self.time):
                last_span = soup.select("body > div.grid-container.accent-blue.margin-top-30px.shadow-soft > div.grid-70.padded-15px.accent-white.bp-content > div > div:nth-child(3) > div > span")[-1]
                if last_span.select_one("a"):
                    next_url = self.start_urls[0] + last_span.select_one("a").get("href")
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

        title = soup.select_one(
            "body > div.grid-container.margin-top-30px.bp-container.shadow-soft.border-white > div > div:nth-child(1) > div.grid-40.padded-15px > h1").text

        pub_list = re.split(' |\n|\t', soup.find("span", class_="metapost").text.strip())

        time_str = ''
        for i in pub_list:
            time_str += (i + ' ')

        image_list = []
        if soup.select("body > div.grid-container.margin-top-30px.bp-container.shadow-soft.border-white > div > div:nth-child(1) > div.grid-60.bp-article-image > img"):
            for img in soup.select("body > div.grid-container.margin-top-30px.bp-container.shadow-soft.border-white > div > div:nth-child(1) > div.grid-60.bp-article-image > img"):
                image_list.append(self.start_urls[0] + img.get("src"))

        body = ''

        for p in soup.select("body > div.grid-container.margin-top-30px.bp-container.shadow-soft.border-white > div > div:nth-child(2) > div > p"):
            body += (p.text + '\n')

        abstract = body.split(".")[0].strip()

        item['category2'] = soup.find("h3",class_="text-green").text
        item["pub_time"] = new_format_time2(time_str)
        item["images"] = image_list
        item["abstract"] = abstract
        item["body"] = body
        # item['category1'] = 'Berita'
        item["title"] = title.strip()

        yield item


