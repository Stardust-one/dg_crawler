# encoding: utf-8

from config.host_config import *
from crawler.items import *
from common.db_keys import WEBSITE_HTML_KEYS
from utils.date_util import DateUtil

class HtmlPipeline:
        '''
        存放HTML的Pipeline
        '''
        def process_item(self, item, spider):
                try:
                        # 丢弃ack
                        if isinstance(item, AckItem):
                                return item
                        # 数据库insert
                        spider.news_db.insert('html', WEBSITE_HTML_KEYS, [item['md5'], item['html'], DateUtil.time_now_formate()])
                        print(item)
                        return item
                except Exception as e:
                        spider.send_log(3, "HtmlPipeline error ==> {} ==> html:{}".format(e, item['html']))