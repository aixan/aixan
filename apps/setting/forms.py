from django.forms import ModelForm
from apps.setting.models import Menu


class MenuForm(ModelForm):

    class Meta:
        model = Menu
        # 定义表单包含的字段
        fields = ('pid', 'title', 'icon', 'href', 'target', 'sort', 'status', 'desc', 'created_by')
