from django.conf.urls import url
from django.urls import path
from apps.exec import views

app_name = 'apps.exec'

urlpatterns = [
    url('task.html', views.task, name="task"),
    url('template.html', views.template, name="template"),
    path('template_get/', views.template_get, name='template_get'),
    path('template_edit/', views.template_edit, name='template_edit'),
    path('template_type/', views.template_type, name='template_type'),
    path("template_search/", views.template_search, name='template_search'),
    url("schedule.html", views.schedule, name='schedule'),
    path("schedule_get/", views.schedule_get, name='schedule_get'),
    path("schedule_type", views.schedule_type, name='schedule_type'),
    path("schedule_edit/", views.schedule_edit, name='schedule_edit'),
    path("schedule_view/", views.schedule_view, name='schedule_view'),
    path("schedule_history/", views.schedule_history, name='schedule_history'),
    path("schedule_hist/", views.schedule_hist, name='schedule_hist'),
]
