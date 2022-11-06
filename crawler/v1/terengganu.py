from crawler.spiders import BaseSpider
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
import requests

# author: 曾嘉祥
class terengganuSpider(BaseSpider):
    name = 'terengganu'
    allowed_domains = ['terengganu.gov.my']
    start_urls = ['http://www.terengganu.gov.my/']
    website_id = 428  # 网站的id(必填)
    language_id = 2036  # 所用语言的id
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu=soup.find(class_='sp-megamenu-parent menu-fade hidden-sm hidden-xs').find_all(class_='sp-menu-item sp-has-child')[-1].select_one('.sp-dropdown-items').select('li')
        del menu[-1]
        for i in menu:
            meta = {'category1': i.select_one('a').text, 'category2': None, 'title': None, 'abstract': None, 'images': None}
            url = ('http://www.terengganu.gov.my' + i.select_one('a').get('href'))
            yield Request(url,callback=self.parse_category,meta=meta)

    def parse_category(self, response):
        flag = True
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select_one('.blog').find_all('article')
        for i in menu:  # 该目录初始的文章
            url = 'http://www.terengganu.gov.my' + i.select_one('.entry-header h2 a').get('href')
            response.meta['title'] =i.select_one('.entry-header h2 a').text.strip()
            time = i.select_one('.published time').get('datetime')
            time = time.replace('T',' ')
            adjusted_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})", time).group(0)
            response.meta['time'] = adjusted_time
            if self.time is None or Util.format_time3(adjusted_time) >= int(self.time):
                yield Request(url=url, meta=response.meta, callback=self.parse_detail)
            else:
                flag = False
                self.logger.info("时间截止")

        if flag:
            try:
                nextPage = 'http://www.terengganu.gov.my'+ soup.select_one('.pagination').select('li')[-1].select_one('a').get('href')
                yield Request(nextPage,callback=self.parse_category,meta=response.meta)
            except:
                self.logger.info('Next page no more!')

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['images'] = ['http://www.terengganu.gov.my'+ soup.find(class_='entry-image full-image').select_one('img').get('src')] if soup.find(class_='entry-image full-image').select_one('img').get('src') else None
        # p_list = []
        # if soup.find('div', class_="texto dont-break-out").select('p') :
        #     all_p = soup.find('div', class_="texto dont-break-out").select('p')
        #     for paragraph in all_p:
        #         p_list.append(paragraph.text)
        #     body = '\n'.join(p_list)
        soup_str = str(soup.select_one('.sppb-addon-content'))
        soup_replace = soup_str.replace('<br/>', '\n')
        while True:
            index_begin = soup_replace.find("<")
            index_end = soup_replace.find(">", index_begin + 1)
            if index_begin == -1:
                break
            soup_replace = soup_replace.replace(soup_replace[index_begin:index_end + 1], "")
        item['body'] = soup_replace
        item['abstract'] = soup_replace[:soup_replace.find('\n')]
        return item