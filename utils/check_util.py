# encoding: utf-8

import os

class CheckUtil():
        '''
        检查工具类
        '''

        @staticmethod
        def check_item(item):
                '''
                检查item格式是否有误
                '''
                if item['language_id'] < 1727 or item['language_id'] > 2272: # language_id的正常范围。
                        return True
                return None

        @staticmethod
        def check_path(path):
                '''
                验证路径是否存在，不存在则创建并返回。
                '''
                if not os.path.isdir(path):
                      os.makedirs(path)
                return path