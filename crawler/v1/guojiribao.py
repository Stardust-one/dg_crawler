from crawler.spiders import BaseSpider
# 此文件包含的头文件不要修改
import scrapy
from utils.util_old import *
from crawler.items import *
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
import requests
from datetime import datetime
import json

#将爬虫类名和name字段改成对应的网站名
#author 陈宣齐
class guojiribao(BaseSpider):
    name = 'guojiribao'
    website_id = 11 # 网站的id(必填)
    language_id = 1813 # 所用语言的id
    start_urls = ['http://www.guojiribao.com']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.find('ul', id='main-menu').find_all('li')[:-1]:
            yield Request(i.find('a').get('href'),callback=self.parse_2, meta={'category1':i.find('a').text})
        Data = {
            'action': 'anwp_pg_load_more_posts',
            'args[posts_to_show]': 'latest',
            'args[include_ids]': '',
            'args[exclude_ids]': '',
            'args[exclude_by_category]': '',
            'args[filter_by_category]': '8',
            'args[filter_by_tag]': '',
            'args[filter_by_post_format]': 'all',
            'args[filter_by_author]': '',
            'args[published_in_last_days]': '0',
            'args[limit]': '3',
            'args[offset]': '22',
            'args[grid_cols]': '1',
            'args[grid_cols_tablet]': '2',
            'args[grid_cols_mobile]': '1',
            'args[grid_thumbnail_size]': 'large',
            'args[show_category]': 'yes',
            'args[category_limit]': '2',
            'args[show_date]': 'yes',
            'args[show_author]': 'yes',
            'args[show_comments]': '',
            'args[card_height]': '180',
            'args[show_excerpt]': 'yes',
            'args[layout]': 'f',
            'args[show_read_more]': '',
            'args[read_more_label]': '',
            'args[read_more_class]': '',
            'args[post_image_width]': '1_3',
            'args[show_post_icon]': 'yes',
            'args[query_source]': 'posts',
            'args[related_posts]': '',
            'args[related_posts_order]': '',
            'loaded': '25',
            'qty': '3',
            '_ajax_nonce': '0e5c6f4b38'
        }
        post_url = 'https://guojiribao.com/wp-admin/admin-ajax.php'
        category = ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
        for i in category:
            Data['args[filter_by_category]'] = i
            yield scrapy.FormRequest(url=post_url,formdata=Data,callback=self.parse_post,meta={'category':i,'loaded':'25'})

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        for i in page_soup.find_all('div', class_='d-flex anwp-row flex-wrap anwp-pg-light-grid anwp-pg-posts-wrapper')[
                 1:]:
            if i.find('div',
                      class_='anwp-pg-post-teaser anwp-pg-post-teaser--layout-f anwp-col-lg-12 anwp-col-sm-6 anwp-col-12 d-flex position-relative') is not None:
                for news in i.find_all('div',
                                       class_='anwp-pg-post-teaser anwp-pg-post-teaser--layout-f anwp-col-lg-12 anwp-col-sm-6 anwp-col-12 d-flex position-relative'):
                    title = news.find('div', class_='anwp-pg-post-teaser__title anwp-font-heading my-auto').text.strip(
                        '\n').strip('			')
                    pub_time = news.find('span', class_='posted-on m-0').find('time').get('datetime').split('T')[
                                   0] + ' 00:00:00'
                    img = news.find('div', class_='anwp-pg-post-teaser__thumbnail-img').get('style').split('(')[
                        1].strip(')')
                    url = news.find_all('a')[-1].get('href')
                    if self.time == None or Util.format_time3(pub_time) >= int(self.time):
                        yield Request(url=url,callback=self.parse_3,meta={'category1':response.meta['category1'],'title':title,'img':img,'pub_time':pub_time})
                    else:
                        self.logger.info("时间截止")

    def parse_post(self,response):
        rep = json.loads(response.text)
        category = response.meta['category']
        loaded = str(int(response.meta['loaded']) + 3)
        Data = {
            'action': 'anwp_pg_load_more_posts',
            'args[posts_to_show]': 'latest',
            'args[include_ids]': '',
            'args[exclude_ids]': '',
            'args[exclude_by_category]': '',
            'args[filter_by_category]': category,
            'args[filter_by_tag]': '',
            'args[filter_by_post_format]': 'all',
            'args[filter_by_author]': '',
            'args[published_in_last_days]': '0',
            'args[limit]': '3',
            'args[offset]': '22',
            'args[grid_cols]': '1',
            'args[grid_cols_tablet]': '2',
            'args[grid_cols_mobile]': '1',
            'args[grid_thumbnail_size]': 'large',
            'args[show_category]': 'yes',
            'args[category_limit]': '2',
            'args[show_date]': 'yes',
            'args[show_author]': 'yes',
            'args[show_comments]': '',
            'args[card_height]': '180',
            'args[show_excerpt]': 'yes',
            'args[layout]': 'f',
            'args[show_read_more]': '',
            'args[read_more_label]': '',
            'args[read_more_class]': '',
            'args[post_image_width]': '1_3',
            'args[show_post_icon]': 'yes',
            'args[query_source]': 'posts',
            'args[related_posts]': '',
            'args[related_posts_order]': '',
            'loaded': loaded,
            'qty': '3',
            '_ajax_nonce': '0e5c6f4b38'
        }
        post_url = 'https://guojiribao.com/wp-admin/admin-ajax.php'
        post_soup = BeautifulSoup(rep['data']['html'], 'lxml')
        last_time = ''
        for news in post_soup.find_all('div',
                                       class_='anwp-pg-post-teaser anwp-pg-post-teaser--layout-f anwp-col-lg-12 anwp-col-sm-6 anwp-col-12 d-flex position-relative'):
            title = news.find('div', class_='anwp-pg-post-teaser__title anwp-font-heading my-auto').text.strip(
                '\n').strip('			')
            pub_time = news.find('span', class_='posted-on m-0').find('time').get('datetime').split('T')[
                           0] + ' 00:00:00'
            last_time = pub_time
            img = news.find('div', class_='anwp-pg-post-teaser__thumbnail-img').get('style').split('(')[1].strip(')')
            url = news.find_all('a')[-1].get('href')
            category1 = news.find('div',class_='anwp-pg-category__wrapper d-flex align-items-center anwp-pg-post-teaser__category-wrapper mb-1 mr-2').text
            if self.time == None or Util.format_time3(pub_time) >= int(self.time):
                yield Request(url=url,callback=self.parse_3,meta={'category1':category1,'title':title,'img':img,'pub_time':pub_time})
            else:
                self.logger.info("时间截止")
        if self.time == None or Util.format_time3(last_time) >= int(self.time):
            yield scrapy.FormRequest(url=post_url,formdata=Data,callback=self.parse_post,meta={'category':category,'loaded':str(loaded)})
        else:
            self.logger.info("加载更多,时间截止")


    def parse_3(self,response):
        item = NewsItem()
        new_soup = BeautifulSoup(response.text,'lxml')
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['body'] = ''
        for i in new_soup.find_all('p', style='text-align: justify;'):
            item['body'] += i.text
        item['abstract'] = item['body'].split('。')[0]
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item
