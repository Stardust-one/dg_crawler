# encoding: utf-8

import json
from utils.date_util import DateUtil
from utils.format_util import FormatUtil
from common.db_keys import *
from crawler.items import *

class SqlPipeline:
        '''
        录入SQL的Pipeline
        '''

        def process_item(self, item, spider):
                try:
                        # 丢弃ack
                        if isinstance(item, AckItem):
                                return item

                        # md5生成
                        item['md5'] = FormatUtil.url_md5(item['request_url'])
                        # images生成
                        item['images'] = json.dumps(item['images'])
                        # cole_time生成
                        item['cole_time'] = DateUtil.time_now_formate()
                        # 数据库insert
                        keylist = []
                        valuelist = []
                        for i in WEBSITE_NEWS_KEYS:
                                if i not in item:
                                        continue
                                keylist.append(i)
                                valuelist.append(item[i])
                        spider.news_db.insert('news', keylist, valuelist)
                        spider.send_log(1, "网页抓取成功 ==> url:<{}>".format(item['response_url']))
                        return item
                except Exception as e:
                        item['html'] = 'html'
                        spider.send_log(3, "SqlPipeline error ==> {} ==> item:{}".format(e, item))