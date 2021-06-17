from django import forms
from django.forms import Form, ModelForm, fields
from django.core.exceptions import ValidationError
from apps.user.models import User


class RegisterForm(Form):
    username = fields.CharField(
        required=True,
        min_length=3,
        max_length=18,
        error_messages={
            "required": "用户名不可以为空！",
            "min_length": "用户名不能低于3位！",
            "max_length": "用户名不能超过18位！"
        }
    )
    password1 = fields.CharField(
        required=True,
        min_length=3,
        max_length=18,
        error_messages={
            "required": "密码不可以空",
            "min_length": "密码不能低于3位！",
            "max_length": "密码不能超过18位！"
        }
    )
    password2 = fields.CharField(required=False)
    email = fields.EmailField(
        required=True,
        error_messages={
            "required": "邮箱不可以为空！"
        },
    )

    def clean_password2(self):
        if not self.errors.get("password1"):
            if self.cleaned_data["password2"] != self.cleaned_data["password1"]:
                raise ValidationError("您输入的密码不一致，请重新输入！")
            return self.cleaned_data


class UserForm(Form):
    id = forms.CharField(required=True)
    username = forms.CharField(required=True)
    name = forms.CharField(required=True)
    sex = fields.CharField(required=True)
    phone = fields.CharField(required=True)
    email = fields.EmailField(required=True)
    card_id = fields.CharField(required=True)
    home_address = fields.CharField(required=True)
    desc = fields.CharField(required=False,)

    def clean(self):
        if not self.errors.get("username"):
            data = User.objects.filter(username=self.cleaned_data['username']).first()
            if data and data.id != self.cleaned_data['id']:
                raise ValidationError("用户名已存在")

        if not self.errors.get("phone"):
            data = User.objects.filter(phone=self.cleaned_data['phone']).first()
            if data and data.id != self.cleaned_data['id']:
                raise ValidationError("手机号已存在")

        if not self.errors.get("email"):
            data = User.objects.filter(email=self.cleaned_data['email']).first()
            if data and data.id != self.cleaned_data['id']:
                raise ValidationError("邮箱已存在")

        return self.cleaned_data


class ChangepwdForm(Form):
    old_password = forms.CharField(
        required=True,
        label=u"原密码",
        error_messages={'required': u'请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u"原密码",
            }
        ),
    )
    new_password = forms.CharField(
        required=True,
        label=u"新密码",
        error_messages={'required': u'请输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u"新密码",
            }
        ),
    )
    again_password = forms.CharField(
        required=True,
        label=u"确认密码",
        error_messages={'required': u'请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u"确认密码",
            }
        ),
     )
