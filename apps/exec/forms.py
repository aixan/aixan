from django.forms import ModelForm
from apps.exec.models import Exec


# Profile的表单类
class Template(ModelForm):

    class Meta:
        model = Exec
        # 定义表单包含的字段
        fields = ('name', 'types', 'body', 'desc')
