from django.db import models
import json
from apps.user.models import User
from apps.lib.utils import human_datetime


class Alarm(models.Model):
    MODES = (
        ('1', '微信'),
        ('2', '短信'),
        ('3', '钉钉'),
        ('4', '邮件'),
        ('5', '企业微信'),
    )
    STATUS = (
        ('1', '报警发生'),
        ('2', '故障恢复'),
    )
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    notify_mode = models.CharField(max_length=255)
    notify_grp = models.CharField(max_length=255)
    status = models.CharField(max_length=2, choices=STATUS)
    duration = models.CharField(max_length=50)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Alarm %r>' % self.name

    class Meta:
        db_table = 'alarms'
        ordering = ('-id',)


class Group(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=255, blank=True, null=True)
    contacts = models.ManyToManyField(to='Contact')
    # contacts = models.TextField(null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<AlarmGroup %r>' % self.name

    class Meta:
        db_table = 'alarm_groups'
        ordering = ('-id',)


class Contact(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    ding = models.CharField(max_length=255, blank=True, null=True)
    wx_token = models.CharField(max_length=255, blank=True, null=True)
    qy_wx = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<AlarmContact %r>' % self.name

    class Meta:
        db_table = 'alarm_contacts'
        ordering = ('-id',)
