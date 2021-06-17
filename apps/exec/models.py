from django.db import models
from apps.user.models import User
from apps.lib.utils import human_datetime


class Exec(models.Model):
    name = models.CharField(max_length=50)
    types = models.CharField(max_length=50)
    body = models.TextField()
    desc = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Exec %r>' % self.name

    class Meta:
        db_table = 'exec'
        ordering = ('-id',)
        verbose_name = "模板"
        verbose_name_plural = "模板"


class History(models.Model):
    STATUS = (
        (0, '成功'),
        (1, '异常'),
        (2, '失败'),
    )
    task_id = models.IntegerField()
    status = models.SmallIntegerField(choices=STATUS)
    run_time = models.CharField(max_length=20)
    output = models.TextField()

    class Meta:
        db_table = 'schedule_history'
        ordering = ('-id',)
        verbose_name = "任务历史"
        verbose_name_plural = "任务历史"


class Schedule(models.Model):
    TRIGGERS = (
        ('date', '一次性'),
        ('calendarinterval', '日历间隔'),
        ('cron', 'UNIX cron'),
        ('interval', '普通间隔')
    )
    name = models.CharField(max_length=50)
    types = models.CharField(max_length=50)
    command = models.TextField()
    targets = models.TextField()
    trigger = models.CharField(max_length=20, choices=TRIGGERS)
    trigger_args = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    latest = models.ForeignKey(History, on_delete=models.PROTECT, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)

    rst_notify = models.CharField(max_length=255, null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Schedule %r>' % self.name

    class Meta:
        db_table = 'schedule'
        ordering = ('-id',)
        verbose_name = "任务"
        verbose_name_plural = "任务"
