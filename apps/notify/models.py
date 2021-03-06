from django.db import models
from django.core.cache import cache
from apps.lib.utils import human_datetime
import time


class Notify(models.Model):
    TYPES = (
        ('1', '通知'),
        ('2', '待办'),
    )
    SOURCES = (
        ('monitor', '监控中心'),
        ('schedule', '任务计划'),
        ('flag', '应用发布'),
    )
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=10, choices=SOURCES)
    types = models.CharField(max_length=2, choices=TYPES)
    content = models.CharField(max_length=255, null=True)
    unread = models.BooleanField(default=True)
    link = models.CharField(max_length=255, null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)

    @classmethod
    def make_notify(cls, source, types, title, content=None, with_quiet=True):
        if not with_quiet or time.time() - cache.get('spug:notify_quiet', 0) > 3600:
            cache.set('aixan:notify_quiet', time.time())
            cls.objects.create(source=source, title=title, types=types, content=content)

    def __repr__(self):
        return '<Notify %r>' % self.title

    class Meta:
        db_table = 'notify'
        ordering = ('-id',)
