# encoding: utf-8

import scrapy
from libs.mysql import Mysql
from scrapy.exceptions import CloseSpider
from crawler.items import *
from config.db_config import *
from libs.logger import Logger
from utils.format_util import FormatUtil
from utils.find_util import FindUtil

class BaseSpider(scrapy.Spider):
    '''
    爬虫基类，所有的爬虫都应继承自此类。
    '''

    name = 'base_spider'  # 爬虫名
    website_id = 0 # 网站的id(必填)
    language_id = 0 # 所用语言的id
    start_urls = [] # 起始网页
    time = None # 截止时间
    proxy = '00' # 默认proxy
    mini_logger = None # 自带logger
    is_http = 0 # 默认为0


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            # 参数设置
            for i in kwargs.keys():
                setattr(self, i, kwargs[i])
            # self.is_http = FindUtil.find_is_http(self.website_id)
            # logger初始化
            self.mini_logger = Logger(self.name)
            # time初始化
            self.time = FormatUtil.format_time(self.time)
            # 数据库设置
            news_db_conf = kwargs["db"] if kwargs.get("db") in WEBSITE_CONFIG_LIST.keys() else "00"
            self.news_db = Mysql(WEBSITE_CONFIG_LIST[news_db_conf])
        except Exception as e:
            self.send_log(3, "爬虫初始化失败 ==> {}".format(e))
            raise CloseSpider('强制停止')

    def make_header(self, request):
        '''
        制作请求头，传入request中。
        request.headers[key] = value
        '''

        if "Headers" not in request.meta.keys():
            return 
        if not isinstance(request.meta["Headers"], dict):
            self.send_log(2, "请求头格式错误 ==> " + str(request.meta["Headers"]))
            return 
        for key,value in request.meta["Headers"].items():
            request.headers[key] = value

    def make_cookie(self, request):
        '''
        制作cookie，传入request中。
        '''
        # TODO: 此方法未完善
        if request.meta != None and "Cookies" in request.meta.keys():
            request.cookies = request.meta["Cookies"]

    def parse(self, response):
        return AckItem()

    def send_log(self, level, log):
        '''
        批量输出log，
        level：1为info，2为warnning，3为error
        '''
        if level == 1:
            self.logger.info(log)
            self.mini_logger.info(log)
            print('INFO: {}'.format(log))
        elif level == 2:
            self.logger.warning(log)
            self.mini_logger.warning(log)
            print('WARNING: {}'.format(log))
        elif level == 3:
            self.logger.error(log)
            self.mini_logger.error(log)
            print('ERROR: {}'.format(log))