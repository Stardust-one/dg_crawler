# encoding: utf-8

# sql语句
SQL_FILTER = "select md5 from news where website_id = {} and md5 = '{}'"
SQL_DEVELOPMENT_SELECT = 'SELECT * FROM development WHERE is_open = 1 ORDER BY run_time'
SQL_DEVELOPMENT_TIME_UPDATE = "UPDATE development SET run_time = '{}' WHERE name = '{}'"
SQL_DEVELOPMENT_INSERT = "INSERT into development VALUES({},'{}','{}',2,1,NULL,{},NOW(),NOW());"
SQL_DEVELOPMENT_SPIDERNAME_SELECT = "SELECT name FROM development"
# 第一次插入，有四个默认值如上。
# 共9字段(website_id,name,proxy,level,is_open,remark,is_http,start_time,run_time)
