from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response

# author ： 詹婕妤

class UnionsupremecourtSpider(BaseSpider):
    name = 'unionsupremecourt'
    allowed_domains = ['www.unionsupremecourt.gov.mm']
    start_urls = ['https://www.unionsupremecourt.gov.mm/news',
                  'https://www.unionsupremecourt.gov.mm/announcements']
    website_id = 1378
    language_id = 2065
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select_one('div.headline > h1').text.strip()
        for i in soup.find_all(class_='blog-item'):
            url = i.find(class_='blog-text').find('a').get('href')
            title = i.find(class_='blog-text').find('a').text.strip()
            pub_time = i.find('ul').find('li').text.strip()
            yield Request(url, callback=self.parse_item, meta={'category1': category1, 'title': title, 'pub_time': pub_time})
        pub = soup.find_all(class_='blog-item')[-1].find('ul').find('li').text.strip()
        if soup.select('ul.pagination > li')[-1].find('a'):
            next_url = soup.select('ul.pagination > li')[-1].find('a').get('href')
            if self.time == None or Util.format_time3(pub) >= int(self.time):
                yield Request(next_url,callback=self.parse,meta=response.meta)
            else:
                self.logger.info('时间截止')

    def parse_item(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        images = [img.get('src') for img in soup.find(class_='single-blog').find_all('img')] if soup.find(class_='single-blog').find_all('img') else []
        if soup.find(class_='single-blog').find('span'):
            for a in soup.find(class_='single-blog').find('span').find_all('a'):
                images.append(a.get('href'))
        body = ''
        if soup.find(class_='single-blog').find_all('p'):
            for p in soup.find(class_='single-blog').find_all('p'):
                body += p.text.strip() + '\n'

        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = images
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        # self.logger.info(item)
        return item


