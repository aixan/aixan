from django.urls import path
from . import views


app_name = 'apps.host'

urlpatterns = [
    path('host.html', views.host, name='host'),
    path('get_type/', views.get_type, name='get_type'),
    path('get_host/', views.get_host, name='get_host'),
    path('edit_host.html', views.edit_host, name='edit_host'),
    path('search/', views.search, name='search'),
]
