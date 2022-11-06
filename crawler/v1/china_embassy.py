from crawler.spiders import BaseSpider
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup

# author 刘鼎谦
class ChinaEmbassySpider(BaseSpider):
    name = 'china_embassy'
    # allowed_domains = ['http://mm.china-embassy.org/chn/']
    start_urls = ['http://mm.china-embassy.org/chn/',
                  'http://mm.china-embassy.org/chn/sgxw/']

    website_id = 1449  # 网站的id(必填)
    language_id = 1813   # 语言
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_pub = soup.select('.Text_Center li')[-1].text[-11:-1]+' 00:00:00'
        flag=True
        if self.time is None or Util.format_time3(last_pub) > int(self.time):
            if re.findall('chn/sgxw', response.url):
                for i in soup.select('#chnllist a'):
                    meta={'category1':'使馆新闻','category2':None}
                    url = 'http://mm.china-embassy.org/chn/sgxw/' + i.get('href')[2:]
                    yield Request(url=url, meta=meta, callback=self.parse_sgxw)
                for i in soup.select('.Text_Center > ul a'):
                    meta={'category1':'使馆新闻','category2':None}
                    url = 'http://mm.china-embassy.org/chn/sgxw/' + i.get('href')[2:]
                    yield Request(url=url, callback=self.parse_item, meta=meta)
            elif len(response.url.split('/')) != 5:
                for i in soup.select('.Text_Center > ul a'):
                    meta={'category1':soup.select('.Top_Title1 a')[1].text ,'category2':soup.select('.Top_Title1 a')[-1].text}
                    url = response.url.split('default')[0] + i.get('href')[2:]
                    yield Request(url=url, callback=self.parse_item, meta=meta)
            else:
                for i in soup.select('.Text_Left > ul:nth-of-type(2)  a'):
                    meta = {'category1': '中缅关系', 'category2': i.text}
                    if meta['category2'] == '经济商务' or meta['category2'] == '军事交往':
                        continue
                    url =response.url.split('default')[0] + i.get('href')[1:]
                    yield Request(url=url, meta=meta)
                for i in soup.select('.Text_Left > ul:nth-of-type(3)  a'):
                    meta = {'category1': '了解缅甸', 'category2': i.text}
                    if meta['category2'] == '政治经济'or meta['category2'] == '文化教育':
                        continue
                    url = response.url.split('default')[0]+ i.get('href')[1:]
                    yield Request(url=url, meta=meta)
        else:
            self.logger.info("时间截止")
            flag=False
        if flag:
            try:
                countPage=re.findall(r'\d+//共多少页',str(soup.select_one('#pages')))[0].split('//')[0]
                for i in range(2,int(countPage)):
                    url=response.url.split('default')[0] + f'default_{i}.htm'  # 'default_' + str(i)+ '.htm'
                    yield Request(url)
            except:
                self.logger.info("Next page no more")

    def parse_sgxw(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.Text_Center > ul a'):
            meta = {'category1': '使馆新闻', 'category2': None}
            url = 'http://mm.china-embassy.org/chn/sgxw/' + i.get('href')[2:]
            yield Request(url=url, callback=self.parse_item, meta=meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('#News_Body_Title').text
        item['images'] = [response.url.split('/t')[0]+'/'+i.get('src')[2:] for i in soup.select('#article img')]
        tt =soup.select_one('#News_Body_Time').text.split('/')
        item['pub_time'] ="{}-{}-{} 00:00:00".format(tt[0],tt[1],tt[2])
        item['category2'] = response.meta['category2']
        item['body'] ='\n'.join([i.text.strip() for i in soup.select('#article p')])
        item['abstract'] = soup.select('#article p')[0].text.strip()
        return item