from django.conf.urls import url
from django.urls import path
from apps.domains import views

app_name = 'apps.domains'

urlpatterns = [
    url('api.html', views.api, name="api"),
    url('api_get/', views.api_get, name="api_get"),
    url('api_edit/', views.api_edit, name="api_edit"),

    url('domains.html', views.domains, name="domains"),
    url('domains_add/', views.domains_add, name="domains_add"),

    url('parsing_get/', views.parsing_get, name="parsing_get"),
    url('parsing_edit/', views.parsing_edit, name="parsing_edit"),

    url('ca.html', views.ca, name="ca"),
    url('get_ca', views.get_ca, name="get_ca"),
]
