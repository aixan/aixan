from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_SCHEDULER_SHUTDOWN, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from django_redis import get_redis_connection
from apps.exec.models import Schedule, History
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.db import close_old_connections
from apps.exec.utils import auto_clean_schedule_history
from apps.exec.executors import dispatch
from apps.lib.utils import human_datetime
from apps.exec.utils import send_fail_notify
from apps.notify.models import Notify
import logging
import json


class Task:
    timezone = settings.TIME_ZONE
    week_map = {
        '*': '*',
        '7': '6',
        '0': '6',
        '1': '0',
        '2': '1',
        '3': '2',
        '4': '3',
        '5': '4',
        '6': '5',
    }

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=self.timezone, executors={'default': ThreadPoolExecutor(30)})
        self.scheduler.add_listener(
            self._handle_event,
            EVENT_SCHEDULER_SHUTDOWN | EVENT_JOB_ERROR | EVENT_JOB_MAX_INSTANCES | EVENT_JOB_EXECUTED)

    @classmethod
    def parse_trigger(cls, trigger, trigger_args):
        if trigger == 'interval':
            return IntervalTrigger(seconds=int(trigger_args), timezone=cls.timezone)
        elif trigger == 'date':
            return DateTrigger(run_date=trigger_args, timezone=cls.timezone)
        elif trigger == 'cron':
            args = json.loads(trigger_args) if not isinstance(trigger_args, dict) else trigger_args
            minute, hour, day, month, week = args['rule'].split()
            week = cls.week_map[week]
            return CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=week,
                               start_date=args['start'], end_date=args['stop'])
        else:
            raise TypeError(f'unknown schedule policy: {trigger!r}')

    def _handle_event(self, event):
        close_old_connections()
        obj = SimpleLazyObject(lambda: Schedule.objects.filter(pk=event.job_id).first())
        if event.code == EVENT_SCHEDULER_SHUTDOWN:
            logging.warning(f'EVENT_SCHEDULER_SHUTDOWN: {event}')
            Notify.make_notify('schedule', '1', '调度器已关闭', '调度器意外关闭，请排查故障！')
        elif event.code == EVENT_JOB_MAX_INSTANCES:
            logging.warning(f'EVENT_JOB_MAX_INSTANCES: {event}')
            send_fail_notify(obj, '达到调度实例上限，一般为上个周期的执行任务还未结束，请增加调度间隔或减少任务执行耗时')
        elif event.code == EVENT_JOB_ERROR:
            logging.warning(f'EVENT_JOB_ERROR: job_id {event.job_id} exception: {event.exception}')
            send_fail_notify(obj, f'执行异常：{event.exception}')
        elif event.code == EVENT_JOB_EXECUTED:
            if event.retval:
                score = 0
                for item in event.retval:
                    score += 1 if item[1] else 0
                history = History.objects.create(
                    task_id=event.job_id,
                    status=2 if score == len(event.retval) else 1 if score else 0,
                    run_time=human_datetime(event.scheduled_run_time),
                    output=json.dumps(event.retval)
                )
                Schedule.objects.filter(pk=event.job_id).update(latest=history)
                if score != 0:
                    send_fail_notify(obj)

    def _init_builtin_jobs(self):
        # self.scheduler.add_job(auto_clean_alarm_records, 'cron', hour=0, minute=1)
        # self.scheduler.add_job(auto_clean_login_history, 'cron', hour=0, minute=2)
        self.scheduler.add_job(auto_clean_schedule_history, 'cron', hour=0, minute=3)
        # self.scheduler.add_job(auto_update_status, 'interval', minutes=5)

    def _init(self):
        self.scheduler.start()
        self._init_builtin_jobs()
        for item in Schedule.objects.filter(is_active=True, deleted_by__id__isnull=True):
            trigger = self.parse_trigger(item.trigger, item.trigger_args)
            self.scheduler.add_job(
                dispatch,
                trigger,
                id=str(item.id),
                args=(item.command, eval(item.targets)),
            )

    def run(self):
        rds_cli = get_redis_connection()
        self._init()
        rds_cli.delete(settings.SCHEDULE_KEY)
        logging.warning('Running scheduler')
        while True:
            _, data = rds_cli.brpop(settings.SCHEDULE_KEY)
            task = json.loads(data)
            print(task)
            if task['action'] in ('add', 'modify'):
                trigger = self.parse_trigger(task['trigger'], task['trigger_args'])
                self.scheduler.add_job(
                    dispatch,
                    trigger,
                    id=str(task['id']),
                    args=(task['command'], eval(task['targets'])),
                    replace_existing=True
                )
            elif task['action'] == 'remove':
                job = self.scheduler.get_job(str(task['id']))
                if job:
                    job.remove()
