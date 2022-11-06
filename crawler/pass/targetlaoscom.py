from utils.date_util import DateUtil
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
from crawler.items import NewsItem
from crawler.spiders import BaseSpider


# author: 武洪艳,  # check: 刘鼎谦
class TargetlaoscomSpider(BaseSpider):
    name = 'targetlaoscom'
    website_id = 1637
    language_id = 2005
    # allowed_domains = ['targetlaos.com/']
    start_urls = ['https://targetlaos.com/']  # https://targetlaos.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu-item-3304 > ul > li > a')
        for category in categories:
            category1 = category.text
            if category1 == 'ຂ່າວ ພາຍໃນປະເທດ':
                for i in soup.select('#menu-item-3304 > ul > li > ul > li > a'):
                    category_url = i.get('href')
                    yield Request(url=category_url, callback=self.parse_page,
                                  meta={'category1': category1, 'category2': i.text})
            else:
                for li in categories:
                    category_url = li.get('href')
                    yield Request(url=category_url, callback=self.parse_page,
                                  meta={'category1': category1, 'category2': None})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if self.time is not None:
            t = soup.select('div.post-listing > article > p > span')[-1].text.split('/')
            last_time = "{}-{}-{}".format(t[2], t[1], t[0]) + ' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.select('#main-content > div.content-wrap > div > div.post-listing h2 > a')
            for article in articles:
                article_url = article.get('href')
                title = article.text
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'title': title, 'category1': response.meta['category1'],
                                    'category2': response.meta['category2']})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('#tie-next-page a') is not None:
                next_page = soup.select_one('#tie-next-page a').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        tt = soup.select_one('#the-post > div.post-inner > p > span.tie-date').text.split('/')
        item['pub_time'] = "{}-{}-{}".format(tt[2], tt[1], tt[0]) + ' 00:00:00'
        item['images'] = [img.get('src') for img in soup.select('#the-post > div.post-inner > div.entry img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('#the-post > div.post-inner > div.entry') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
