from django.db import models
from apps.user.models import User
from apps.lib.utils import human_datetime
import json


class MonT(models.Model):
    name = models.CharField(max_length=50)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<MonT %r>' % self.name

    class Meta:
        db_table = 'mon_t'
        ordering = ('-id',)


class MonApp(models.Model):
    name = models.CharField(max_length=50)
    mont = models.ManyToManyField(MonT, verbose_name='监控模板')

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<MonApp %r>' % self.name

    class Meta:
        db_table = 'mon_app'
        ordering = ('-id',)


class MonItem(models.Model):
    name = models.CharField(max_length=50)
    types = models.CharField(max_length=50, verbose_name='监控模板')
    mona = models.ManyToManyField(MonApp, verbose_name='应用集')
    mont = models.ForeignKey(MonT, on_delete=models.CASCADE, verbose_name='监控模板')

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<MonItem %r>' % self.name

    class Meta:
        db_table = 'mon_item'
        ordering = ('-id',)
