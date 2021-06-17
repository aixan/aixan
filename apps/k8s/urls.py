from django.urls import path, re_path, include
from apps.k8s_api import views
from apps.k8s import views
app_name = 'apps.k8s'

urlpatterns = [
    path('k8s.html', views.k8s, name='k8s'),

    path('k8s_view/', views.K8s_View, name='k8s_view'),
    path('edit_k8s/', views.edit_k8s, name='edit_k8s'),
    path('add_ca/', views.add_ca, name='add_ca'),
    path('add_config/', views.add_config, name='add_config'),
    path('auth.html/', views.auth, name='auth'),
    path('k8s_auth/', views.K8s_Auth, name='k8s_auth'),
    path('add_auth/', views.add_auth, name='add_auth'),
    path('edit_auth/', views.edit_auth, name='edit_auth'),

    path('get_k8s/', views.get_k8s, name='get_k8s'),
]
