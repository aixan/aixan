from django.db import models
from apps.user.models import User
from apps.lib.utils import human_datetime


class Api(models.Model):
    name = models.CharField(max_length=50)
    Cloud = (
        ("1", "阿里云"),
        ("2", "腾讯云")
    )
    cloud = models.CharField(max_length=50, choices=Cloud, verbose_name="云厂商")
    region = models.CharField(max_length=50)
    key = models.CharField(max_length=50)
    secret = models.CharField(max_length=50)
    desc = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Dom_api %r>' % self.name

    class Meta:
        db_table = 'api'
        ordering = ('-id',)
        verbose_name = "接口"
        verbose_name_plural = "接口"


class Domains(models.Model):
    api = models.ForeignKey(Api, on_delete=models.CASCADE)
    domain = models.CharField(max_length=50, verbose_name="域名")
    dns1 = models.CharField(max_length=50)
    dns2 = models.CharField(max_length=50)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Domains %r>' % self.domain

    class Meta:
        db_table = 'domains'
        ordering = ('id',)
        verbose_name = "域名"
        verbose_name_plural = "域名"


class Parsing(models.Model):
    domain = models.ForeignKey(Domains, on_delete=models.CASCADE)
    RR = models.CharField(max_length=255)
    Type = models.CharField(max_length=50)
    Value = models.CharField(max_length=50)
    TTL = models.CharField(max_length=50, blank=True, null=True)
    Priority = models.CharField(max_length=50, blank=True, null=True)
    Line = models.CharField(max_length=50, blank=True, null=True)
    RecordId = models.CharField(max_length=50)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Parsing %r>' % self.domain

    class Meta:
        db_table = 'domains_parsing'
        ordering = ('id',)
        verbose_name = "解析"
        verbose_name_plural = "解析"


class Ca(models.Model):
    domain = models.CharField(max_length=255)
    etime = models.DateTimeField(auto_now_add=False, blank=True, null=True, verbose_name="到期")
    e_day = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Ca %r>' % self.domain

    class Meta:
        db_table = 'CA'
        ordering = ('id',)
