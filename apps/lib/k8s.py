from kubernetes import client, config
from django.shortcuts import redirect
import os
from apps.user.models import User
from kubernetes.stream import stream
from datetime import date, timedelta
from apps.k8s.models import K8s, Auth
from channels.generic.websocket import WebsocketConsumer
from threading import Thread


def dt_format(timestamp):
    time = date.strftime((timestamp + timedelta(hours=8)), "%Y-%m-%d %H:%M:%S")
    return time


def auth_config(user, hostname):
    user = User.objects.get(username=user)
    if user.is_superuser:
        data = K8s.objects.get(hostname__hostname=hostname)
        config.load_kube_config(r"%s" % data.config)
    else:
        data = Auth.objects.get(user__username=user, hostname__hostname__hostname=hostname)
        configuration = client.Configuration()
        configuration.host = "https://{}:6443".format(hostname)  # APISERVER地址
        configuration.ssl_ca_cert = str(data.hostname.ca)  # CA证书
        configuration.verify_ssl = True  # 启用证书验证
        configuration.api_key = {"authorization": "Bearer " + data.token}  # 指定Token字符串
        client.Configuration.set_default(configuration)
