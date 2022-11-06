# encoding: utf-8
import re
import time

from fire.core import Fire
from libs.mysql import Mysql
from config.db_config import *
from common.sql import *
from utils.date_util import DateUtil
import os
import fire
import eventlet


class Main:
    def __init__(self, db='01', time='days_ago:3'):
        self.db = db
        self.time = time
        self.common_db = None
        self.run()

    def run(self):
        command = 'scrapy crawl {} -a db={} -a time={} -a proxy={}'
        while True:
            eventlet.monkey_patch()
            try:
                with eventlet.Timeout(10800, False):  # 超过3h停止
                    self.common_db = Mysql(COMMON_WEBSITE_CONFIG)
                    self.insert_dev()
                    for i in self.common_db.select(SQL_DEVELOPMENT_SELECT):
                        if i[1]+'.py' in os.listdir('crawler/v1') or i[1]+'.py' in os.listdir('crawler/pass'):
                            self.common_db.execute(SQL_DEVELOPMENT_TIME_UPDATE.format(DateUtil.time_now_formate(), i[1]))
                            command_ = command.format(i[1], self.db, self.time, i[2])
                            print(command_)
                            os.system(command_)
                            continue
                print("-"*20+"time out"*5+"-"*20)
                self.common_db = None
                # time.sleep(3600*5)  # 测试，循环一次，暂 停5h，
            except Exception as e:
                print("主进程出错 ==> {}".format(e))
                self.common_db = None

    def insert_dev(self):
        passList=os.listdir('crawler/pass')
        passList.remove("__init__.py")
        if "__pycache__" in passList:
            passList.remove('__pycache__')
        if passList:
            try:
                deployedSpis =[i[0] for i in self.common_db.select(SQL_DEVELOPMENT_SPIDERNAME_SELECT)]
                for i in passList:
                    name = i[:-3]
                    if name not in deployedSpis:
                        spiderFile=open(file=f'crawler/pass/{i}',mode='r',encoding='utf-8').read()
                        tmp = re.findall("proxy[ =']+\d+",spiderFile)[0] if re.findall("proxy[ =']+\d+",spiderFile) else None
                        proxy =re.findall('\d+',tmp)[0] if tmp else '00'
                        is_http = 1 if re.findall("is_http[ '=1]",spiderFile) else 0
                        website_id = re.findall('\d+',re.findall("website_id[ =]+\d+", spiderFile)[0])[0]
                        sql = SQL_DEVELOPMENT_INSERT.format(website_id, name, proxy, is_http)
                        print(sql)
                        self.common_db.execute(sql)
            except Exception as e:
                print("Something wrong with the spiders in folder pass:",end='')
                print(e)
        else:
            print("Accomplished Spiders Were Not Found")
# 主进程函数
# python -m main
# python -m main --db=00 --time=now
if __name__ == "__main__":
    fire.Fire(Main)