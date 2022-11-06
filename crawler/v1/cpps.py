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
class cppsSpider(BaseSpider):
    name = 'cpps'
    allowed_domains = ['cpps.org.my']
    start_urls = ['http://cpps.org.my/publication/']
    website_id = 705  # 网站的id(必填)
    language_id = 1866  # 所用语言的id
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

    
          
        

    # def parse(self, response):
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     menu=soup.find(class_='sp-megamenu-parent menu-fade hidden-sm hidden-xs').find_all(class_='sp-menu-item sp-has-child')[-1].select_one('.sp-dropdown-items').select('li')
    #     del menu[-1]
    #     for i in menu:
    #         meta = {'category1': i.select_one('a').text, 'category2': None, 'title': None, 'abstract': None, 'images': None}
    #         url = ('http://www.terengganu.gov.my' + i.select_one('a').get('href'))
    #         yield Request(url,callback=self.parse_category,meta=meta)

    def parse(self, response):
        flag = True
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
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select_one('.lists-container').select('.single-pub-bg')
        for i in menu:  # 该目录初始的文章
            meta = {'category1': i.select_one('.title a').text, 'category2': None, 'title': i.select_one('.title a').text, 'abstract': None, 'images': None}
            url = i.select_one('.title a').get('href')
            time = i.select_one('.byline').text
            adjusted_time = re.search(r"([a-zA-Z]* \d{1,2}, \d{4})", time).group(0)
            mon=month[adjusted_time.split()[0]]
            year=adjusted_time.split()[2]
            day=adjusted_time.split()[1].replace(',', '')
            adjusted_time=year+'-'+mon+'-'+day+' 00:00:00'
            meta['time'] = adjusted_time

            if self.time is None or Util.format_time3(adjusted_time) >= int(self.time):
                yield Request(url=url, meta=meta, callback=self.parse_detail)
            else:
                flag = False
                self.logger.info("时间截止")

        if flag:
            try:
                nextPage = soup.find(class_='next page-numbers').get('href')
                yield Request(nextPage,callback=self.parse,meta=response.meta)
            except:
                self.logger.info('Next page no more!')

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['images'] = []
        p_list = []
        if soup.find(class_='col-md-9 col-sm-12 post').select('div') :
            all_p = soup.find(class_='col-md-9 col-sm-12 post').select('div')[1].select('p')
            for paragraph in all_p:
                p_list.append(paragraph.text.strip())
            body = '\n'.join(p_list)
            item['abstract'] = p_list[0]
            item['body'] = body
        # soup_str = str(soup.select_one('.sppb-addon-content'))
        # soup_replace = soup_str.replace('<br/>', '\n')
        # while True:
        #     index_begin = soup_replace.find("<")
        #     index_end = soup_replace.find(">", index_begin + 1)
        #     if index_begin == -1:
        #         break
        #     soup_replace = soup_replace.replace(soup_replace[index_begin:index_end + 1], "")
        # item['body'] = soup_replace
        # item['abstract'] = soup_replace[:soup_replace.find('\n')]
        return item

# def time_adjustment(input_time):
#     month = {
#             'January': '01',
#             'February': '02',
#             'March': '03',
#             'April': '04',
#             'May': '05',
#             'June': '06',
#             'July': '07',
#             'August': '08',
#             'September': '09',
#             'October': '10',
#             'November': '11',
#             'December': '12'
#         }