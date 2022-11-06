from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
from datetime import datetime

# author ： 詹婕妤
#  连接超时，网站原因。
class UsdporgmmSpider(BaseSpider):
    name = 'usdporgmm'
    allowed_domains = ['www.usdp.org.mm']
    start_urls = ['http://www.usdp.org.mm/']
    website_id = 1387
    language_id = 2065
    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'local_crawler',
    #     'password': 'local_crawler',
    #     'db': 'local_dg_test'
    # }
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        for i in soup.select('#menu-main-menu-my > li')[1:]:
            category1 = i.find('a').text.strip()
            if category1 != 'စာအုပ္စင္':
                if i.find(class_='sub-menu'):
                    for a in i.select('ul.sub-menu > li'):
                        category2 = a.find('a').text.strip()
                        url = a.find('a').get('href')
                        yield Request(url,callback=self.parse_list,meta={'category1':category1,'category2':category2})
                else:
                    url = i.find('a').get('href')
                    yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': None})

    def parse_list(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        for i in soup.select('#content > article'):
            title = i.find(class_='entry-title').text.strip()
            if i.find(class_='post-teaser-more'):
                url = i.find(class_='post-teaser-more').find('a').get('href')
                response.meta['title'] = title
                yield Request(url,callback=self.parse_news,meta=response.meta)
            else:
                item['body'] = i.find(class_='entry-content clearfix').text.strip()
                item['images'] = [img.get('src') for img in i.find(class_='entry-content clearfix').find_all('img')] if i.find(class_='entry-content clearfix').find_all('img') else []
                item['category1'] = response.meta['category1']
                item['category2'] = response.meta['category2']
                item['title'] = title
                item['abstract'] = item['body'].split('\n')[0]
                item['pub_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield item

        if soup.find(class_='wp-paginate'):
            if soup.find(class_='wp-paginate').find(class_='next'):
                next_url = soup.find(class_='wp-paginate').find(class_='next').get('href')
                if next_url:
                    if soup.select('#content > article')[-1].find(class_='post-teaser-more'):
                        last_url = soup.select('#content > article')[-1].find(class_='post-teaser-more').find('a').get('href')
                        response.meta['next_url'] = next_url
                        yield Request(last_url,callback=self.parse_page,meta=response.meta)
                    else:  # 最后一个新闻没有url的直接翻页
                        yield Request(next_url,callback=self.parse_list,meta=response.meta)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        if soup.find(class_='entry-date published'):
            pub_time = soup.find(class_='entry-date published').text.strip()
            pub_time = Util.format_time2(pub_time)
        if self.time == None or Util.format_time3(pub_time) >= int(self.time):
            yield Request(response.meta['next_url'],callback=self.parse_list,meta=response.meta)
        else:
            self.logger.info('时间截止')

    def parse_news(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        pub_time = Util.format_time2(soup.find(class_='entry-date published').text.strip())
        images = [img.get('src') for img in soup.find('article').find_all('img')] if soup.find('article').find_all('img') else []
        body = ''
        if soup.find(class_='entry-content clearfix').find_all('p'):
            for p in soup.find(class_='entry-content clearfix').find_all('p'):
                body += p.text.strip() + '\n'
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = pub_time
        item['images'] = images
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        yield item



