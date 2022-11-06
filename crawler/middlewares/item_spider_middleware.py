# encoding: utf-8

from scrapy import signals
import pymysql
from utils.check_util import *
from crawler.items import *
from scrapy.http import Request

# TODO: 将extention分离出来
class ItemSpiderMiddleware:
        '''
        item爬虫中间件，其中也附加了logger extention的处理
        '''

        @classmethod
        def from_crawler(cls, crawler):
                s = cls()
                crawler.signals.connect(s.spider_error, signal=signals.spider_error)
                crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
                return s

        def process_spider_output(self, response, result, spider): 
                for i in result:
                        try:
                                # 若为Request则抛出
                                if isinstance(i,Request):
                                        yield i
                                        continue
                                # item包装
                                i['request_url'] = response.request.url
                                i['response_url'] = response.url
                                i['website_id'] = spider.website_id
                                if not i.get('language_id'):
                                        i['language_id'] = spider.language_id
                                if not i.get('images'):
                                        i['images'] = []
                                if not i.get('html'):
                                        i['html'] = response.text
                                #检查item
                                check = CheckUtil.check_item(i)
                                if not check:
                                        yield i
                                else:
                                        spider.send_log(2, 'item格式有误，{} ==> {}'.format(check, i))
                                        yield AckItem()
                        except Exception as e:
                                spider.send_log(3, "ItemSpiderMiddleware error ==> {} ==> url:<{}>".format(e, response.url))

        # 错误日志输出
        def spider_error(self, failure, response, spider):
                spider.send_log(3, 'spider error ==> {} ==> url:<{}>'.format(failure.value, response.url))
                spider.mini_logger.error(failure)

        # 爬虫关闭日志输出
        def spider_closed(self, spider, reason):
                spider.mini_logger.info('爬虫结果 ==> ' + str(spider.crawler.stats.get_stats()))
