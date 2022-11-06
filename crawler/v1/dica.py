from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import time
from datetime import datetime


# author: 詹婕妤
class DicaSpider(BaseSpider):
    name = 'dica'
    allowed_domains = ['www.dica.gov.mm']
    start_urls = ['https://www.dica.gov.mm/en/news']
    website_id = 1366
    language_id = 1866
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    month = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12,
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sept': 9,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        category1 = soup.select_one('#page-title').text.strip()
        for i in soup.find(class_='view-content').select('div'):
            if i.select_one('div.read-more') is not None:
                url = i.select_one('div.read-more > a').get('href')
                yield Request(url,callback=self.parse_news,meta={'category1':category1})

        pub_time = soup.find(class_='view-content').find_all(class_='news-date')[-1].text.strip().split('on')[-1].strip().split()
        pub_time = time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(pub_time[2]), self.month[pub_time[1]], int(pub_time[0])).timetuple())

        if self.time == None or Util.format_time3(pub_time) >= int(self.time):
            if soup.select_one('ul.pager > li.pager-next.odd'):
                next_url = 'https://www.dica.gov.mm' + soup.select_one('ul.pager > li.pager-next.odd > a').get('href')
                yield Request(next_url)
            if soup.select_one('ul.pager > li.pager-next.even'):
                next_url = 'https://www.dica.gov.mm' + soup.select_one('ul.pager > li.pager-next.even > a').get('href')
                yield Request(next_url)
        else:
            self.logger.info('时间截止')

    def parse_news(self, response):
        item = NewsItem()
        soup = BeautifulSoup(response.text,'html.parser')
        item['category1'] = response.meta['category1']
        item['category2'] = None
        title = soup.find(class_='pane-title block-title').text.strip()
        # self.logger.info(title)
        images = [img.get('src') for img in soup.select_one('div.block-content > article').find_all('img')] if soup.select_one('div.block-content > article').find_all('img') else []
        # self.logger.info(images)
        pub_time = soup.select_one('div.news-details-date').text.split('on')[-1].strip().split(' ')
        item['pub_time'] = time.strftime("%Y-%m-%d %H:%M:%S",datetime(int(pub_time[2]),self.month[pub_time[1]],int(pub_time[0])).timetuple())
        body = ''
        for p in soup.select_one('div.block-content > article').find(class_='field-item even').select('p'):
            body += p.text.strip() + '\n'
        # self.logger.info(body)
        if soup.select('div.field-item.even > div:nth-child(1) > div > div'):
            for div in soup.select('div.field-item.even > div:nth-child(1) > div > div'):
                body += div.select_one('div').text.strip() + '\n'
        item['title'] = title
        item['images'] = images
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        # self.logger.info(item)
        yield item

