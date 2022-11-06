from bs4 import BeautifulSoup
from utils.date_util import DateUtil
from crawler.spiders import BaseSpider
from crawler.items import *
from scrapy.http.request import Request
import execjs
import re
import copy

from common.date import ENGLISH_MONTH as month
from common.header import MOZILLA_HEADER

# author: rht\ldq\why
class AseanorgSpider(BaseSpider):
    name = 'aseanorg'
    website_id = 1802
    language_id = 1866
    start_urls = [
        'https://asean.org/category/news/',
        'https://asean.org/category/statements-meetings/',
        'https://asean.org/category/speeches/',
        'https://asean.org/category/news-events/'
    ]
    custom_settings = {"DEFAULT_REQUEST_HEADERS": MOZILLA_HEADER}

    def start_requests(self):
        for i in self.start_urls:
            category1 = i.split('/')[-2]
            yield Request(url=i,meta={'Headers':MOZILLA_HEADER,"category1":category1})

    def getCookie(self, response):
        # 用re把js代码扣下来
        js = re.findall(r'<script>(.*)</script>', response.text)[0]
        # 因为execjs是函数驱动的，所以得用函数包装一下，获取r的值
        ctx = execjs.compile(('function fun(){' + js + '}').replace('e(r)', 'return r'))
        js = ctx.call('fun')
        # 同上
        ctx = execjs.compile(
            ('function fun(){' + js + '}').replace('document.cookie', 'out').replace('location.reload()', 'return out'))
        # 添加cookie
        cookie = ctx.call('fun')
        return cookie

    def parse(self, response):
        if (re.findall(r'<title>(.*)</title>', response.text)[0] == 'You are being redirected...'):
            header = copy.deepcopy(MOZILLA_HEADER)
            header["cookie"] = self.getCookie(response)
            # 往request传请求头的方式是直接给meta的Headers传个列表，里面是要修改的请求头字段
            # 如果Headers里没有user-agent字段会刷新ua，传了就不会刷新而是用你传进去的那个
            yield Request(url=response.url, meta={'Headers': header,"category1":response.meta['category1']}, dont_filter=True)
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('article > a')
            for article in articles:
                article_url = article.get('href')
                # 后面这些也是一样
                # print(article_url)
                yield Request(url=article_url, callback=self.parse_item, meta={'Headers':response.meta['Headers'],'category1':response.meta['category1']})
            next_page = soup.select_one('.page-numbers.next').get('href')
            yield Request(url=next_page, meta={'Headers': response.meta['Headers'],'category1':response.meta['category1']}, callback=self.parse_page, dont_filter=True)

    def parse_page(self, response):  # 文章数量少，且新闻列表没有发布时间，不写时间截止
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article > a')
        for article in articles:
            article_url = article.get('href')
            yield Request(url=article_url, callback=self.parse_item,meta=response.meta,dont_filter=True)
        next_page = soup.select_one('.page-numbers.next').get('href')
        yield Request(url=next_page, meta=response.meta, callback=self.parse_page,dont_filter=True)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('div > h2').text.strip()
        try:
            tt = soup.find(class_='elementor-icon-list-item elementor-repeater-item-ca9fc7d elementor-inline-item').find('a').get('href').split('/')
            item['pub_time'] = "{}-{}-{} 00:00:00".format(tt[-4],tt[-3],tt[-2])
        except:
            item['pub_time'] = DateUtil.time_now_formate()
        item['images'] = [img.get('src') for img in soup.select('.elementor-section-wrap .elementor-image img')]
        item['body'] = '\n'.join([paragraph.text.strip()
                                  for paragraph in soup.select('.elementor-widget-container p')
                                    if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
