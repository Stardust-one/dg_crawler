from crawler.spiders import BaseSpider
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request
import re

# author 刘鼎谦
class NwinSpider(BaseSpider):
    name = 'newswing'
    allowed_domains = ['newswing.com']
    start_urls = ['https://newswing.com/']
    website_id = 1047  # 网站的id(必填)
    language_id = 1930  # 所用语言的id
    proxy = '01'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-main-navigation >li a')[1:]:
            meta = {'category1': i.text, 'category2': ''}
            yield Request(url=i.get('href'), meta=meta, callback=self.parse_page)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        for i in soup.select('.post-details'):  # 每页的文章及其摘要
            strtt = i.find(class_='date meta-item tie-icon').text  # strtt 形如 '05/01/2021'
            pub_time = strtt.split('/')[2] + '-' + strtt.split('/')[1] + '-' + strtt.split('/')[0] + ' 00:00:00'
            if self.time is None or Util.format_time3(pub_time) >= int(self.time):
                response.meta['pub_time'] = pub_time
                yield Request(url=i.select_one('.post-title a').get('href'), meta=response.meta,
                              callback=self.parse_item)
            else:
                flag = False
                self.logger.info('时间截止')
                break
        if flag:
            try:
                nextPage = soup.select_one('div.pages-nav a').get('href') if soup.select_one('div.pages-nav a').get(
                    'href') else None
                pageNum = re.findall('\d+',nextPage)[0]
                if nextPage:  # 有下一页就翻页
                    yield Request(url=nextPage, meta=response.meta, callback=self.parse_page)
                    for i in range(2, 180):
                        url = nextPage.replace(pageNum,str(i))
                        yield Request(url=url, meta=response.meta, callback=self.parse_page)
            except:
                self.logger.info('Next page no more')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('div.entry-header>h1').text
        # strtt = soup.select_one('#single-post-meta > span:nth-of-type(2)').text  # strtt 形如 '05/01/2021'
        item['pub_time'] = response.meta[
            'pub_time']  # strtt.split('/')[2]+'-'+strtt.split('/')[1]+'-'+strtt.split('/')[0]+' 00:00:00'
        item['images'] = [i.get('src') for i in soup.select('#the-post img')]
        item['body'] = '\n'.join([p.text.strip() for p in soup.select('#the-post p')])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
