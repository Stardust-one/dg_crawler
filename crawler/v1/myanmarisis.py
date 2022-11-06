from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from scrapy.http import Request, Response
import re
import time
from bs4 import BeautifulSoup


# author:刘鼎谦  finished_time: 2021-07-10 静态 文章很少：56篇
class MyanmarisisSpider(BaseSpider):
    name = 'myanmarisis'
    allowed_domains = ['www.myanmarisis.org']
    start_urls = ["https://www.myanmarisis.org/events"]
    # 'https://www.myanmarisis.org/news/',  这个栏目下的新闻来自https://www.irrawaddy.com/————将作为一个独立爬虫来写——————news标题下发布时间不好找

    website_id = 1421 # 网站的id(必填)
    language_id = 1866  # 英文语言
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
          
        

    def parse(self, response):   # 新闻列表 有完整新闻
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        last_pub_time= Util.format_time2(soup.select('#page-content-wrapper > div.container.section-1 > div > div.col-lg-9.col-md-9.col-sm-9.col-xs-12 > div > div h5')[-1].text)
        if self.time is None or Util.format_time3(last_pub_time) >= int(self.time):
            all_pub_time = [Util.format_time2(i.text) for i in soup.select('#page-content-wrapper > div.container.section-1 > div > div.col-lg-9.col-md-9.col-sm-9.col-xs-12 > div > div h5')]
            all_title = [i.text.strip() for i in soup.select('.lk-tle')]
            all_images = ['https://www.myanmarisis.org'+i.get('src') for i in soup.select('.img-responsive.lk-img')]
            all_body = [i.text.strip() for i in soup.select('#page-content-wrapper > div.container.section-1 > div > div.col-lg-9.col-md-9.col-sm-9.col-xs-12 > div p')]
            for i in range(9):
                item=NewsItem()
                item['pub_time'] = all_pub_time[i]
                item['images'] = [all_images[i]]
                item['title'] = all_title[i]
                item['body'] = all_body[i]
                item['category1']='event'
                item['category2'] =None
                item['abstract'] = all_body[i].split('\n')[0]
                yield item
        else:
            self.logger.info('时间截止！')
            flag = False
        if flag:
            try:
                nextPage=soup.select_one('.active ~ li a').get('href')
                yield Request(url=nextPage)
            except:
                self.logger.info("Next page no more.")


