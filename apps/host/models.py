from django.db import models
# from libs import ModelMixin, human_datetime
# from apps.account.models import User
# from apps.setting.utils import AppSetting
from apps.lib.exec import SSH
from apps.setting.utils import AppSetting
from apps.lib.utils import human_datetime
from apps.user.models import User


class Host(models.Model):
    name = models.CharField(max_length=50, verbose_name="名称")
    system = models.CharField(max_length=50, verbose_name="操作系统")
    types = models.CharField(max_length=50, verbose_name="类别")
    hostname = models.CharField(max_length=50, verbose_name="主机名/IP")
    port = models.IntegerField(verbose_name="端口号")
    username = models.CharField(max_length=50, verbose_name="登录用户")
    pkey = models.TextField(null=True, verbose_name="主机密钥")
    desc = models.CharField(max_length=255, null=True, verbose_name="备注")

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Host %r>' % self.name

    @property
    def private_key(self):
        return self.pkey or AppSetting.get('private_key')

    def get_ssh(self, pkey=None):
        pkey = pkey or self.private_key
        return SSH(self.hostname, self.port, self.username, pkey)

    class Meta:
        db_table = 'hosts'
        ordering = ('-id',)
        verbose_name = "主机"
        verbose_name_plural = "主机"
