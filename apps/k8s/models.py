from django.db import models
# from libs import ModelMixin, human_datetime
# from apps.account.models import User
# from apps.setting.utils import AppSetting
# from libs.ssh import SSH
from apps.host.models import Host
from apps.user.models import User
from apps.lib.utils import human_datetime


class K8s(models.Model):
    name = models.CharField(max_length=50, verbose_name="集群名称")
    hostname = models.OneToOneField(Host, on_delete=models.CASCADE)
    ca = models.FileField(upload_to='ca/', verbose_name="集群证书", null=True, blank=True)
    config = models.FileField(upload_to='config/', verbose_name="集群认证", null=True, blank=True)
    desc = models.CharField(max_length=255, null=True, verbose_name="备注")

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    class Meta:
        db_table = 'k8s'
        ordering = ('-id',)
        verbose_name = "K8S"
        verbose_name_plural = "K8S"


class Auth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hostname = models.ForeignKey(K8s, on_delete=models.CASCADE)
    token = models.TextField(max_length=500, null=True, blank=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    class Meta:
        db_table = 'k8s_auth'
        ordering = ('id',)
        verbose_name = "K8S授权"
        verbose_name_plural = "K8S授权"
