from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_SCHEDULER_SHUTDOWN, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from django_redis import get_redis_connection
from apps.domains.models import Ca
from django.conf import settings
import logging
from _datetime import datetime
from urllib3.contrib import pyopenssl
import re
import time
import subprocess
from datetime import datetime
from io import StringIO


class Task:

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.data = Ca.objects.all()

    def get_expire(self, domain):
        try:
            f = StringIO()
            comm = f"curl -Ivs https://{domain} --connect-timeout 10"
            result = subprocess.getstatusoutput(comm)
            f.write(result[1])
            m = re.search('start date: (.*?)\n.*?expire date: (.*?)\n.*?common name: (.*?)\n.*?issuer: CN=(.*?)\n',
                          f.getvalue(), re.S)
            start_date = m.group(1)
            expire_date = m.group(2)

            # time 字符串转时间数组
            start_date = time.strptime(start_date, "%b %d %H:%M:%S %Y GMT")
            start_date_st = time.strftime("%Y-%m-%d %H:%M:%S", start_date)
            # datetime 字符串转时间数组
            expire_date = datetime.strptime(expire_date, "%b %d %H:%M:%S %Y GMT")
            expire_date_st = datetime.strftime(expire_date, "%Y-%m-%d %H:%M:%S")

            # 剩余天数
            remaining = (expire_date - datetime.now()).days
            print('开始时间:', start_date_st)
            print('到期时间:', expire_date_st)
            print(f'剩余时间: {remaining}天')
            return True, 200, {'expire_time': str(expire_date_st), 'expire_days': remaining}

        except Exception as e:
            return False, 500, str(e)

    def run(self):
        # rds_cli = get_redis_connection()
        # # self._init()
        # rds_cli.delete(settings.SCHEDULE_KEY)
        logging.warning('Running scheduler')

        for item in self.data:
            intervalTrigger: CronTrigger = CronTrigger(second=10)
            # intervalTrigger = CronTrigger(hour=19, minute=30, second=1)
            self.scheduler.add_job(func=self.get_expire, trigger=intervalTrigger, id=item.domain, args=[item.domain])
        self.scheduler.start()
        while True:
            pass

