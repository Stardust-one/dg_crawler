from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


class LsecuritynewscomSpider(BaseSpider):
    name = 'lsecuritynewscom'
    website_id = 1630
    language_id = 2005
    # allowed_domains = ['www.lsecuritynews.com/']
    start_urls = ['https://www.lsecuritynews.com/']  # https://www.lsecuritynews.com/

    def __init__(self, time=None, *args, **kwargs):
        super(LsecuritynewscomSpider, self).__init__(*args, **kwargs)  # 将这行的DemoSpider改成本类的名称
        self.time = time

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu-main-menu-1 > li > a')
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if self.time is not None:
            t = soup.select('div.td-pb-span8.td-main-content .item-details > div.td-module-meta-info > span.td-post-date')[-1].text.split('/')
            last_time = "{}-{}-{}".format(t[2], t[1], t[0]) + ' 00:00:00'
        if self.time is None or DateUtil.time_now_formate(last_time) >= int(self.time):
            articles = soup.select('div.td-pb-span8.td-main-content .item-details > h3 > a')
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.select('div.td-pb-span8.td-main-content .page-nav.td-pb-padding-side > a')[-1].get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('header > h1').text.strip()
        tt = soup.select_one('header > div > span.td-post-date').text.split('/')
        item['pub_time'] = "{}-{}-{}".format(tt[2], tt[1], tt[0]) + ' 00:00:00'
        item['images'] = [img.get('src') for img in soup.select('div.td-pb-span8.td-main-content img')]
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.td-pb-span8.td-main-content p') if paragraph.text!='' and paragraph.text!=' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item