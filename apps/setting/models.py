from django.db import models
from apps.lib.utils import human_datetime
from apps.user.models import User, Role


class Menu(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    pid = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')  # 父节点
    title = models.CharField(max_length=100, null=True, verbose_name='名称')
    icon = models.CharField(max_length=100, blank=True, null=True, verbose_name='菜单图标')
    href = models.CharField(max_length=100, blank=True, null=True, verbose_name='链接')
    target = models.CharField(max_length=20, null=True, default="_self", verbose_name='链接打开方式')
    sort = models.IntegerField(blank=True, null=True, default=0, verbose_name='菜单排序')
    status = models.BooleanField(blank=True, null=True, default=1, verbose_name='状态(0:禁用,1:启用)')
    desc = models.CharField(null=True, max_length=255, blank=True, verbose_name='备注信息')
    role = models.ManyToManyField(Role, verbose_name="菜单")

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', blank=True, null=True)
    deleted_at = models.CharField(max_length=20, blank=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', blank=True, null=True)

    def __int__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.pid
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)

    class Meta:
        ordering = ['-sort']
        db_table = 'menu'
        verbose_name = '菜单'
        verbose_name_plural = "菜单"


class Setting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField()
    desc = models.CharField(max_length=255, null=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Setting %r>' % self.key

    class Meta:
        db_table = 'settings'
        verbose_name = "设置"
        verbose_name_plural = "设置"

