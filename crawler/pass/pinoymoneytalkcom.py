from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request
from common import date


# author : 武洪艳
class PinoymoneytalkcomSpider(BaseSpider):
    name = 'pinoymoneytalkcom'
    website_id = 1186
    language_id = 1866
    # allowed_domains = ['www.pinoymoneytalk.com/']
    start_urls = ['https://www.pinoymoneytalk.com/']  # https://www.pinoymoneytalk.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('.ast-row header.entry-header')
        if self.time is not None:
            t = articles[-1].select_one('span.posted-on .published').text.replace(',',' ').split(' ')
            last_time = "{}-{}-{}".format(t[4], date.ENGLISH_MONTH[t[1]], t[2]) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= self.time:
            for article in articles:
                tt = article.select_one('span.posted-on .published').text.replace(',', ' ').split(' ')
                pub_time = "{}-{}-{}".format(tt[4], date.ENGLISH_MONTH[tt[1]], tt[2]) + ' 00:00:00'
                article_url = article.select_one('h2 > a').get('href')
                title = article.select_one('h2 > a').text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': 'news', 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('div.nav-links > a.next.page-numbers') == None:
                self.logger.info("no more pages")
            else:
                next_page = soup.select_one('div.nav-links > a.next.page-numbers').get('href')
                yield Request(url=next_page, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('data-src') for img in soup.select('div.entry-content.clear img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.entry-content.clear') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
