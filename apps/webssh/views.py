from django.shortcuts import render, HttpResponse
import time
import random
import hashlib
import os
from django.views.decorators.clickjacking import xframe_options_exempt
from apps.lib.set import user_get
from apps.host.models import Host
from apps.user.models import User


@xframe_options_exempt
def ssh(request):
    if request.method == "GET":
        id = request.GET.get("id")
        return render(request, 'webssh/ssh.html', {"id": id})


@xframe_options_exempt
def pod(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')
    namespace = request.GET.get("namespace")
    pod_name = request.GET.get("pod_name")
    containers = request.GET.get("containers").split(',')  # 返回 nginx1,nginx2，转成一个列表方便前端处理
    # 认证类型和token，用于传递到websocket，websocket根据sessionid获取token，让websocket处理连接k8s认证用
    connect = {'hostname': hostname, 'username': user, 'namespace': namespace, 'pod_name': pod_name, 'containers': containers}
    return render(request, 'webssh/pod.html', {'connect': connect})


@xframe_options_exempt
def exec(request):
    if request.method == "GET":
        host = request.GET.get("host").split(",")
        return render(request, 'webssh/exec.html', {"host": host})


def unique():
    ctime = str(time.time())
    salt = str(random.random())
    m = hashlib.md5(bytes(salt, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()
