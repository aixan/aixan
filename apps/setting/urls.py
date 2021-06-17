from django.conf.urls import url
from django.urls import path
from apps.setting import views

app_name = 'apps.setting'

urlpatterns = [
    url('setting.html', views.setting, name="setting"),
    path('get_key/', views.get_key, name="get_key"),
    path('clear/', views.clear, name='clear'),
    path('get_menu/', views.get_menu, name='get_menu'),
    path('menu.html', views.menu, name='menu'),
    path('menu_set/', views.menu_set, name='menu_set'),
    path('add_menu/', views.add_menu, name='add_menu'),
    path('edit_menu/', views.edit_menu, name='edit_menu'),
]
