from django.urls import path
from apps.accept import views

app_name = 'accept'

urlpatterns = [
    # 接受处理数据
    path('', views.add_number, name='accpet'),
]
