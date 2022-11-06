# encoding: utf-8

from libs.mysql import Mysql
from config.db_config import *

sql = 'SELECT is_http FROM development WHERE website_id = {}'

class FindUtil():

    @staticmethod
    def find_is_http(id):
        db = Mysql(COMMON_WEBSITE_CONFIG)
        result = list(db.select(sql.format(str(id))))
        if not result:
            return 0
        return result[0][0]