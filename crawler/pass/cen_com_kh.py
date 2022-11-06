from bs4 import BeautifulSoup
from crawler.spiders import BaseSpider
from crawler.items import *
from utils.date_util import DateUtil
from scrapy.http.request import Request

month = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }

# author： 曾嘉祥
class cen_com_khSpider(BaseSpider):
    name = 'cen_com_kh'
    website_id = 1876
    language_id = 1982  # 999 是国家id
    allowed_domains = ['cen.com.kh']
    start_urls = ['https://www.cen.com.kh/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        menu = soup.find(id='menu-main-menu-1').select('li')[:-1]
        for i in menu:
            url = i.select_one('a').get('href')
            meta ={
                'category1':i.select_one('.tdb-menu-item-text').text
            }
            yield Request(url=url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if self.time is not None:
            t = soup.select_one('#tdi_68 .td-post-date').text.replace(',', '').split()
            last_time = t[2]+'-'+month[t[0]]+'-'+t[1]+' 00:00:00'
        if self.time is None or DateUtil.formate_time2time_stamp(last_time) >= int(self.time):
            articles = soup.find(class_='td_block_inner tdb-block-inner td-fix-index').find_all(class_='tdb_module_loop td_module_wrap td-animation-stack')
            for article in articles:
                article_url = article.find(class_='entry-title td-module-title').select_one('a').get('href')
                title = article.find(class_='entry-title td-module-title').select_one('a').text
                time_split = article.select_one('.td-post-date').text.replace(',', '').split()
                time = time_split[2]+'-'+month[time_split[0]]+'-'+time_split[1]+' 00:00:00'
                response.meta['title'] = title
                response.meta['time']= time
                yield Request(url=article_url, callback=self.parse_item,meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.find(class_='page-nav td-pb-padding-side').select('a')[-1].get('aria-label') == 'next-page':
                next_page = soup.find(class_='page-nav td-pb-padding-side').select('a')[-1].get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['images'] = [i.get('src') for i in soup.select('.wpb_wrapper img')[1:-1]]
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('.tdb-block-inner.td-fix-index p')])
        item['abstract'] = item['body'].split('\n')[0]
        yield item