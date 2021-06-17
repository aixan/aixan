from django.urls import path
from apps.monitor import views


app_name = 'apps.monitor'

urlpatterns = [
    path('monitor.html', views.monitor, name='monitor'),
    path('get_monitor/', views.get_monitor, name='get_monitor'),
    path('add_test/', views.add_test, name='add_test'),
]
