from django.urls import path
from . import views

app_name = 'apps.webssh'

urlpatterns = [
    path('ssh.html', views.ssh, name="ssh"),
    path('pod.html', views.pod, name="pod"),
    path('exec.html', views.exec, name="exec"),
]
