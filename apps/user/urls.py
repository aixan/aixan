from django.contrib import admin
from django.urls import path, include
from apps.user import views
app_name = 'apps.user'

urlpatterns = [
    path('login.html', views.loginView, name='login'),
    path('logout', views.logoutView, name='logout'),

    path('edit/<str:id>/', views.edit, name='edit'),
    path('password/<str:id>', views.password, name='password'),



    path('role.html', views.role, name='role'),
    path('get_role/', views.get_role, name='get_role'),

    path('account.html', views.account, name='account'),
    path('get_account/', views.get_account, name='get_account'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('active/', views.active, name='active'),
    path('passwd/', views.passwd, name='passwd'),
    path('search_user/', views.search_user, name='search_user'),
    path('get_auth/', views.get_auth, name='get_auth'),
    path('menu_auth/', views.menu_auth, name='menu_auth'),
    path('role_user/', views.role_user, name='role_user'),
]
