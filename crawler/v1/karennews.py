from crawler.spiders import BaseSpider
import json
import scrapy
from scrapy import FormRequest
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup


# author:刘鼎谦  finished_time: 2021-07-13  动态网站
class KarennewsSpider(BaseSpider):
    name = 'karennews'
    start_urls = ['http://karennews.org/category/article/']  # 只有这里栏目下有章，且该url只有1页 （10篇），动态翻页

    post_url = 'http://karennews.org/wp-admin/admin-ajax.php'

    website_id = 1488  # 网站的id(必填)
    language_id = 1866  # English
    formdata = {'action': 'tie_archives_load_more',
                'query': "{'cat':3,'lazy_load_term_meta':true,'posts_per_page':10,'order':'DESC'}",
                'max': '195',
                'page': '2',
                'latest_post': '10',
                'layout': 'masonry',
                'settings': "{'uncropped_image':'jannah-image-post','category_meta':false,'post_meta':true,'excerpt':true,'excerpt_length':'60','read_more':true,'media_overlay':false,'title_length':0,'is_full':false,'is_category':true}"
                }
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        last_pub_time = Util.format_time2(soup.select('#masonry-grid > div .date.meta-item.fa-before')[-1].text.strip())
        if self.time is None or Util.format_time3(last_pub_time) >= int(self.time):
            for i in soup.select('#masonry-grid > div')[:-2]:
                meta = {'title': i.select_one('h2').text.strip(),
                        'time': i.select_one('.date.meta-item.fa-before').text.strip(),
                        'abstract': i.select_one('.entry-content').text.strip()
                        }
                yield Request(url=i.select_one('h2>a').get('href'),callback=self.parse_item, meta=meta)
        else:
            self.logger.info("时间截止")
            flag = False
        if flag:
            yield FormRequest(url=self.post_url, formdata=self.formdata,meta={'current_page':'2'}, callback=self.parse_more)

    def parse_more(self, response):
        soup = BeautifulSoup(json.loads(json.loads(response.text))['code'],'html.parser')
        flag = True
        last_pub_time = Util.format_time2(soup.select('.date.meta-item.fa-before')[-1].text)
        if self.time is None or Util.format_time3(last_pub_time) >= int(self.time):
            for i in soup.select('.container-wrapper.post-element'):
                response.meta['title'] = i.select_one('h2').text.strip(),
                response.meta['abstract'] = i.select_one('.entry-content').text.strip()
                yield Request(url=i.select_one('h2>a').get('href'), callback=self.parse_item, meta=response.meta)
        else:
            self.logger.info("时间截止")
            flag = False

        if flag and int(response.meta['current_page']) < 195:
            response.meta['current_page'] = str(int(response.meta['current_page'])+1)
            self.formdata['latest_post'] = str(int(response.meta['current_page']) * 10)
            self.formdata['page'] = response.meta['current_page']
            ##self.logger.info(json.loads(json.loads(response.text))['code'])
            yield FormRequest(url=self.post_url, formdata=self.formdata, meta=response.meta, callback=self.parse_more)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item =NewsItem()
        item['title'] = response.meta['title']
        item['pub_time'] =Util.format_time2(soup.select_one('.date.meta-item.fa-before').text)
        item['abstract'] = response.meta['abstract']
        item['category1'] = 'article'
        item['category2'] = None
        item['images'] = [i.get('src') for i in soup.select('.featured-area img')]
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('.entry-content.entry.clearfix p')])
        return item