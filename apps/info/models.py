from django.db import models


class Heartbeat(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    time = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    class Meta:
        db_table = 'heartbeat'
        ordering = ('-time',)


class Alarm(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    state = models.CharField(max_length=20, blank=True, null=True, verbose_name="状态")
    IP = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    why = models.CharField(max_length=100, blank=True, null=True, verbose_name="故障原因")
    f_time = models.DateTimeField(auto_now_add=False, blank=True, null=True, verbose_name="故障时间")
    r_time = models.DateTimeField(auto_now=False, null=True, blank=True, verbose_name="恢复时间")
    e_time = models.CharField(max_length=20, blank=True, null=True, verbose_name="持续时间")
    problem = models.CharField(max_length=100, blank=True, null=True, verbose_name="监控项")
    c_state = models.CharField(max_length=20, blank=True, null=True)
    e_id = models.IntegerField(blank=True, null=True, verbose_name="故障ID")

    class Meta:
        db_table = 'alarm'
        ordering = ('-id',)
