from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index'),
    path('home.html', views.home, name='home'),
    path('kubernetes.html', views.kubernetes, name='kubernetes'),
    path('user/', include('apps.user.urls', namespace='user')),
    path('accept/', include('apps.accept.urls', namespace='accept')),
    path('info/', include('apps.info.urls', namespace='info')),
    path('alarm/', include('apps.alarm.urls', namespace='alarm')),
    path('host/', include('apps.host.urls', namespace='host')),
    path('k8s/', include('apps.k8s.urls', namespace='k8s')),
    path('k8s_api/', include('apps.k8s_api.urls', namespace='k8s_api')),
    path('webssh/', include('apps.webssh.urls', namespace='webssh')),
    path('exec/', include('apps.exec.urls', namespace='exec')),
    path('domains/', include('apps.domains.urls', namespace='domains')),
    path("setting.html", views.setting, name='setting'),
    path("monitor/", include('apps.monitor.urls', namespace='monitor')),
    path("setting/", include('apps.setting.urls', namespace='setting'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
