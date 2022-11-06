# encoding: utf-8

import time
import datetime
from common.date import *
import re

class DateUtil():
        '''
        时间工具类
        '''

        @staticmethod
        def time_now_formate():
                '''
                返回当前的格式化时间，格式：%Y-%m-%d %H:%M:%S
                '''
                return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        @staticmethod
        def formate_time2time_stamp(time_):
                '''
                将传入的格式化时间转为时间戳，格式：%Y-%m-%d %H:%M:%S
                '''
                return int(time.mktime(time.strptime(time_, "%Y-%m-%d %H:%M:%S")))

        @staticmethod
        def time_stamp2formate_time(time_):
                '''
                将传入的时间戳转为格式化时间，格式：%Y-%m-%d %H:%M:%S
                '''
                return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time_)))

        @staticmethod
        def time_ago(year=0, month=0, week=0, day=0, hour=0, minute=0, second=0):
                '''
                返回指定时间之前的时间戳
                '''
                stamp = int(time.time()) - second - minute*60 - hour*3600 - day*86400 - week*604800 - month*2592000 - year*31536000
                return (stamp if stamp > 0 else 0)

        @staticmethod
        def format_time_English(data1):
                '''
                格式化各类网站时间字符串，格式：%Y-%m-%d %H:%M:%S
                '''
                # TODO: 未开发完
                data = ''
                list = [i for i in re.split('/| |,|:|\n|\r|\f|\t|\v',data1) if i!='']
                for i in list:
                        data += (i+' ')
                data = data.strip()
                if re.findall(r'\S+ \d+ \d+ \d+ \d+',data) != []:
                        num = 0
                        while list[num] not in ENGLISH_MONTH.keys():
                                num += 1
                        return time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(list[num+2]),ENGLISH_MONTH[list[num]],int(list[num+1]),int(list[num+3]),int(list[num+4])).timetuple())
                elif re.findall(r'\S+ \d+ \d+',data) != []:
                        num = 0
                        while list[num] not in ENGLISH_MONTH.keys():
                                num += 1
                        return time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(list[num+2]),ENGLISH_MONTH[list[num]],int(list[num+1])).timetuple())
                elif re.findall(r'\d+ hours ago',data) != [] or re.findall(r'\d+ hour ago',data) != []:
                        num = 0
                        while re.findall(r'\d+',list[num])==[]:
                                num += 1
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*3600))
                elif re.findall(r'\d+ days ago',data) != [] or re.findall(r'\d+ day ago',data) != []:
                        num = 0
                        while re.findall(r'\d+',list[num])==[]:
                                num += 1
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*86400))
                elif re.findall(r'\d+ weeks ago',data) != [] or re.findall(r'\d+ week ago',data) != []:
                        num = 0
                        while re.findall(r'\d+',list[num])==[]:
                                num += 1
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*604800))
                elif re.findall(r'\d+ months ago',data) != [] or re.findall(r'\d+ month ago',data) != []:
                        num = 0
                        while re.findall(r'\d+',list[num])==[]:
                                num += 1
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*2592000))
                elif re.findall(r'\d+ years ago',data) != [] or re.findall(r'\d+ year ago',data) != []:
                        num = 0
                        while re.findall(r'\d+',list[num])==[]:
                                num += 1
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*31536000))
                else:
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))