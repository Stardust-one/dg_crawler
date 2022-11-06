# encoding: utf-8

import os

from apscheduler.schedulers.blocking import BlockingScheduler
from scripts import report, log_clean
from config.scheduler_config import *

def git_pull():
    os.system("git pull")
    print("pull仓库成功")


# 主调度函数
# python -m scheduler
if __name__ == '__main__':
    sched = BlockingScheduler()
    if is_report:
        sched.add_job(report.run, 'cron', hour=0, minute=10)
    if is_log_clean:
        sched.add_job(log_clean.run, 'cron', args=[3], hour=0, minute=10)
    if is_git_pull:
        sched.add_job(git_pull, 'cron', hour='*/1')
    sched.start()
