# encoding: utf-8

import random
from common.header import *
from common.sql import *
from utils.format_util import FormatUtil
from scrapy.exceptions import IgnoreRequest

class FilterDownloaderMiddleware:
        '''
        过滤器下载中间件
        '''

        def process_request(self, request, spider): 
                try:
                        # 初始化meta
                        if not request.meta:
                                request.meta = {}
                        # url规范化
                        if spider.is_http:
                                url = request.url.replace("https://",'http://')
                        else:
                                url = request.url.replace("http://",'https://')
                        url = url.split('#')[0]
                        request._set_url(url)
                        # request中的dont_filter字段，可以同时越过表查重以及scrapy自带查重
                        # (meta中的dont_filter标记为v1功能，现已废弃)
                        if request.dont_filter == True or request.meta.get('dont_filter', False) == True:
                                md5 = FormatUtil.url_md5(url)
                                sql = SQL_FILTER.format(str(spider.website_id), md5)
                                result = spider.news_db.select(sql)
                        # filter查重
                        else:
                                md5 = FormatUtil.url_md5(url)
                                sql = SQL_FILTER.format(str(spider.website_id), md5)
                                result = spider.news_db.select(sql)
                        if result != ():
                                return IgnoreRequest('filter url')
                        # 添加请求头与cookie
                        spider.make_header(request)
                        spider.make_cookie(request)
                        # 随机user-agent
                        headers_ = request.meta.get("Headers", {})
                        if 'User-Agent' not in headers_ and 'user-agent' not in headers_:
                                request.headers['User-Agent'] = random.sample(UA_LIST, 1)[0]

                        return None
                except Exception as e:
                        spider.send_log(3, "FilterDownloaderMiddleware error ==> {} ==> url:<{}>".format(e, request.url))


            