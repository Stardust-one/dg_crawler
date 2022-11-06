# encoding: utf-8
from bs4 import BeautifulSoup
from utils.date_util import DateUtil
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request


# author 刘鼎谦
class JianhuadailySpider(BaseSpider):
    name = 'jianhuadaily'
    allowed_domains = ['jianhuadaily.com']
    start_urls = ['http://jianhuadaily.com/']

    website_id = 1673
    language_id = 1813

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        if self.time is None:
            for i in soup.select('article'):
                url = i.select_one('.title a').get('href')
                meta = {
                    'pub_time': i.select_one('time').get('datetime')[:-6].replace('T', ' '),
                    'abstract': i.select_one('.post-summary').text.strip(),
                    'title': i.select_one('.title').text.strip(),
                    'category1': i.select_one('span a').text
                }
                if meta['category1'] == '电子报':
                    continue
                yield Request(url=url,meta=meta,callback=self.parse_item)
        else:
            last_pub = soup.select('article time')[-1].get('datetime')[:-6].replace('T',' ')
            if self.time < DateUtil.formate_time2time_stamp(last_pub):  # 传入的时间比新闻发布的时间要早(时间戳要小)，也就是新闻很新
                for i in soup.select('article'):
                    url = i.select_one('.title a').get('href')
                    meta = {
                        'pub_time': i.select_one('time').get('datetime')[:-6].replace('T', ' '),
                        'abstract': i.select_one('.post-summary').text.strip(),
                        'title': i.select_one('.title').text.strip(),
                        'category1': i.select_one('span a').text
                    }
                    if meta['category1'] == '电子报':
                        continue
                    yield Request(url=url, meta=meta, callback=self.parse_item)
            else:
                flag = False
                self.logger.info("时间截止!")
        if flag: # 也就是时间未截止翻页
            nextPage=soup.find(class_='next page-numbers').get('href')
            yield Request(url=nextPage)  # 默认回调给parse()

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item=NewsItem()
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip('\n ') for i in soup.select('article p')])
        item['images'] = [i.get('src') for i in soup.select('article img')]
        return item
