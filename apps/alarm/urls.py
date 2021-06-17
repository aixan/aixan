from django.urls import path
from apps.alarm import views


app_name = 'apps.alarm'

urlpatterns = [
    path('contact', views.contact, name='contact'),
    path('contact_get/', views.contact_get, name='contact_get'),
    path('contact_edit/', views.contact_edit, name='contact_edit'),
    path('group', views.group, name='group'),
    path('group_get/', views.group_get, name='group_get'),
    path('group_edit/', views.group_edit, name='group_edit'),
    path('alarm', views.alarm, name='alarm'),
    path('alarm_get/', views.alarm_get, name='alarm_get'),
]
