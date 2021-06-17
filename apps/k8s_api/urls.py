from django.urls import path, re_path, include
from apps.k8s_api import views

app_name = 'k8s_api'

urlpatterns = [
    path('get_yaml/', views.get_yaml, name='get_yaml'),
    path('get_json/', views.get_json, name='get_json'),
    path('yaml_edit.html', views.yaml_edit, name="yaml_edit"),
    path('json_edit.html', views.json_edit, name="json_edit"),
    path('yaml_add.html', views.yaml_add, name="yaml_add"),
    path('json_add.html', views.json_add, name="json_add"),

    path('namespace.html', views.namespace, name="namespace"),
    path('get_namespace/', views.get_namespace, name='get_namespace'),
    path('node.html', views.node, name="node"),
    path('get_node/', views.get_node, name="get_node"),
    path('pv.html', views.pv, name="pv"),
    path('get_pv/', views.get_pv, name="get_pv"),
    path('add_pv.html', views.add_pv, name="add_pv"),

    path('deployment.html', views.deployment, name="deployment"),
    path('get_deployment/', views.get_deployment, name="get_deployment"),
    path('daemonset.html', views.daemonset, name="daemonset"),
    path('get_daemonset/', views.get_daemonset, name="get_daemonset"),
    path('statefulset.html', views.statefulset, name="statefulset"),
    path('get_statefulset/', views.get_statefulset, name="get_statefulset"),
    path('pod.html', views.pod, name="pod"),
    path('get_pod/', views.get_pod, name="get_pod"),
    path('add_pod.html', views.add_pod, name="add_pod"),
    path('cronjobs.html', views.cronjobs, name="cronjobs"),
    path('get_cronjobs.html', views.get_cronjobs, name="get_cronjobs"),
    path('jobs.html', views.jobs, name="jobs"),
    path('get_jobs.html', views.get_jobs, name="get_jobs"),

    path('service.html', views.service, name='service'),
    path('get_service/', views.get_service, name='get_service'),
    path('ingress.html', views.ingress, name="ingress"),
    path('get_ingress/', views.get_ingress, name="get_ingress"),
    path('pvc.html', views.pvc, name="pvc"),
    path('get_pvc/', views.get_pvc, name="get_pvc"),
    path('configmap.html', views.configmap, name="configmap"),
    path('get_configmap/', views.get_configmap, name="get_configmap"),
    path('secret.html', views.secret, name="secret"),
    path('get_secret/', views.get_secret, name="get_secret"),
]
