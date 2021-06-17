from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from shortuuidfield import ShortUUIDField
from django.db import models
from apps.lib.utils import human_datetime
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.auth.models import Group, Permission


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, email, phone, **kwargs):
        if not username:
            raise ValueError("请输入用户名！")
        if not password:
            raise ValueError("请输入密码！")
        if not phone:
            raise ValueError("请输入手机号！")
        if not email:
            raise ValueError("请输入邮箱地址！")
        user = self.model(username=username, phone=phone, email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password, email, **kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(username, password, email, **kwargs)

    def create_superuser(self, username, password, email, **kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(username, password, email, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    id = ShortUUIDField(primary_key=True)
    username = models.CharField(max_length=15, verbose_name="用户名", unique=True)
    name = models.CharField(max_length=13, verbose_name="姓名", null=True, blank=True)
    sex = models.CharField(max_length=2, verbose_name="性别", null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号码")
    email = models.EmailField(verbose_name="邮箱", null=True, blank=True)
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', verbose_name="用户头像", null=True, blank=True)
    card_id = models.CharField(max_length=30, verbose_name="身份证", null=True, blank=True)
    home_address = models.CharField(max_length=100, null=True, blank=True, verbose_name="地址")
    is_active = models.BooleanField(default=True, verbose_name="激活状态")
    is_staff = models.BooleanField(default=True, verbose_name="是否是员工")
    desc = models.TextField(max_length=500, null=True, blank=True)

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='+', null=True)
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='+', null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    EMAIL_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __repr__(self):
        return '<User %r>' % self.username

    class Meta:
        db_table = 'user'
        ordering = ('-id',)
        verbose_name = "用户"
        verbose_name_plural = "用户"


class Role(models.Model):
    name = models.CharField(max_length=32, verbose_name='角色')
    user = models.ManyToManyField(User, verbose_name='用户', blank=True)
    permission = models.ManyToManyField(Permission, verbose_name="权限")

    created_at = models.CharField(max_length=20, default=human_datetime)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    deleted_at = models.CharField(max_length=20, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', null=True)

    def __repr__(self):
        return '<Role name=%r>' % self.name

    class Meta:
        db_table = 'roles'
        ordering = ('-id',)
        verbose_name = "角色"
        verbose_name_plural = "角色"
