import re
from utils.date_util import DateUtil
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from crawler.items import NewsItem
from crawler.spiders import BaseSpider

# author 刘鼎谦
class NewsduanSpider(BaseSpider):
    api = 'http://www.newsduan.com/newsyun/dynamicList/getdynamicListForWapBBZTContentList.jspx?orderBy=2&pageIndex={}&channelId=2441&channelPageSize=5'

    name = 'newsduan'
    # allowed_domains = ['newsduan.com/newsyun/lwzxw/']
    start_urls = ['http://www.newsduan.com/newsyun/dynamicList/getdynamicListForWapBBZTContentList.jspx?orderBy=2&pageIndex=1&channelId=2441&channelPageSize=5'
]

    website_id = 1669
    language_id = 1002

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in [a.get('href') for a in soup.select('a')]:
            yield Request(url=i, callback=self.parse_item)
        try:
            if response.meta['page']:
                response.meta['page'] +=1
        except:
            response.meta['page'] = 2
        if self.time is not None:
            last_pub = re.findall('\d+-\d+-\d+',soup.select('.has_img_time')[-1].text)[0] +' 00:00:00' if soup.select('.has_img_time') else DateUtil.time_now_formate()
            if self.time < DateUtil.formate_time2time_stamp(last_pub):
                yield Request(url=NewsduanSpider.api.format( response.meta['page']),meta=response.meta)
            else:
                self.logger.info('时间截止')
        else:
            yield Request(url=NewsduanSpider.api.format(response.meta['page']), meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['title'] = soup.select_one('h1').text
        item['category1'] = 'news'
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip(' \n,▲') for i in soup.select('.p_con p') ])
        item['abstract'] = item['title']
        item['pub_time'] = soup.select('.sdata span')[-1].text+':00'
        item['images'] = ['http://www.newsduan.com'+i.get('src') for i in soup.select('.p_con img')]
        yield item
