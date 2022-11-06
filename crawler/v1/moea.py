from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import time
from datetime import datetime

# author ： 詹婕妤

class MoeaSpider(BaseSpider):
    name = 'moea'
    allowed_domains = ['moea.gov.mm']
    start_urls = ['https://moea.gov.mm/']
    website_id = 1376
    language_id = 2065
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        if soup.select_one('#menu-item-841'):
            category1 = soup.select_one('#menu-item-841 > a').text.strip()
            if soup.select_one('#menu-item-845'):
                category2 = soup.select_one('#menu-item-845 > a').text.strip()
                url = soup.select_one('#menu-item-845 > a').get('href')
                yield Request(url,callback=self.parse_list,meta={'category1':category1,'category2':category2,'url':url,'page':1})
            if soup.select_one('#menu-item-847'):
                category2 = soup.select_one('#menu-item-847 > a').text.strip()
                url = soup.select_one('#menu-item-847 > a').get('href')
                yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': category2,'url':url,'page':1})
        if soup.select_one('#menu-item-853'):
            category1 = soup.select_one('#menu-item-853 > a').text.strip()
            url = soup.select_one('#menu-item-854 > a').get('href')
            category2 = soup.select_one('#menu-item-854 > a').text.strip()
            yield Request(url, callback=self.parse_list, meta={'category1': category1, 'category2': category2,'url':url,'page':1})

    def parse_list(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        for i in soup.select('div.isotope.row > div'):
            url = i.select_one('div > div > a').get('href')
            response.meta['title'] = i.select_one('div > div > h3 > a').text.strip()
            pub_time = i.select_one('div > div > div > span.date').text.strip() if i.select_one('div > div > div > span.date') else '0000-00-00 00:00:00'
            response.meta['pub_time'] = Util.format_time2(pub_time)
            yield Request(url,callback=self.parse_news,meta=response.meta)
        pub = Util.format_time2(soup.select('div.isotope.row > div')[-1].select_one('div > div > div > span.date').text.strip())
        if soup.select('div.pagination'):
            page_all = soup.select('div.pagination > ul > li')[-1].find('a').get('href').rsplit('/',1)[-1]
            if self.time == None or Util.format_time3(pub) >= int(self.time):
                if response.meta['page'] < int(page_all):
                    response.meta['page'] += 1
                    next_url = response.meta['url'] + '/page/' + str(response.meta['page'])
                    yield Request(next_url,callback=self.parse_list,meta=response.meta)
            else:
                self.logger.info('时间截止')

    def parse_news(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        item = NewsItem()
        images = []
        image = [img.get('data-src') for img in soup.find(class_='post-content').find_all('img')] if soup.find(class_='post-content').find_all('img') else []
        if image != []:
            for img in image:
                if img != None:
                    images.append(img)
        body = ''
        if soup.select('div.post-content > p'):
            for p in soup.select('div.post-content > p'):
                body += p.text.strip() + '\n'
        if soup.select('div.post-content > table'):
            for tr in soup.select('div.post-content > table > thead > tr'):
                for td in tr.select('td'):
                    body += td.text.strip() + '\n'
        if soup.find(class_='elementor-section-wrap'):
            for div in soup.select('div.elementor-section-wrap > section'):
                if div.find(class_='elementor-text-editor elementor-clearfix'):
                    for p in div.select('div.elementor-text-editor.elementor-clearfix > p'):
                        body += p.text.strip() + '\n'

        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = images
        item['body'] = body
        item['abstract'] = body.split('\n')[0]
        return item

