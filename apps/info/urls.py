from django.urls import path
from . import views

app_name = 'apps.info'

urlpatterns = [
    path('alarm.html', views.alarm),
    path('get_page/', views.get_page),
    path('search_page/', views.search_page),
    path('delete_page/', views.delete_page),
    path("update_page/", views.update_page),
]
