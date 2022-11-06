# encoding: utf-8

import re
import time
import hashlib
from utils.date_util import DateUtil

class FormatUtil():
    '''
    格式化工具类
    '''

    @staticmethod
    def format_time(time_):
        if not time_:
            return None
        if time_.isdigit():
            return int(time_)
        if time_ == 'now':
            return int(time.time())
        days = re.findall(r'days_ago:(\d+)', time_)
        if days:
            return DateUtil.time_ago(day=int(days[0]))

    @staticmethod
    def url_md5(url):
        m = hashlib.md5()
        m.update(url.encode(encoding='utf-8'))
        return m.hexdigest()