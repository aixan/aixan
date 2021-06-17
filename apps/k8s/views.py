from django.shortcuts import render
import hashlib
import json
import os
import random
from datetime import datetime
import OpenSSL
import yaml
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from kubernetes import client
from apps.lib.utils import human_datetime
from apps.lib.set import user_get
from apps.host.models import Host
from apps.k8s.models import K8s, Auth
from apps.lib.k8s import dt_format, auth_config
from apps.user.models import User
import threading
import paramiko


def error(e):
    status = getattr(e, "status")
    if status == 403:
        data = {'code': 1, 'msg': "没有访问权限"}
    else:
        data = {'code': 1, 'msg': "获取数据失败"}
    return data


def k8s(request):
    return render(request, 'k8s/k8s.html')


def auth(request):
    return render(request, 'k8s/k8s_auth.html')


def K8s_Auth(request):
    data = Auth.objects.filter(deleted_by__id__isnull=True)
    dataCount = data.count()
    pageIndex = request.GET.get("pageIndex")
    pageSize = request.GET.get("pageSize")

    li_st = []
    res = []
    for item in data:
        di_ct = {'id': item.id, 'username': item.user.username, 'name': item.hostname.name,
                 'hostname': item.hostname.hostname.hostname, 'token': item.token}
        li_st.append(di_ct)

    pageInator = Paginator(li_st, pageSize)
    context = pageInator.page(pageIndex)
    for item in context:
        res.append(item)
    data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
    return HttpResponse(json.dumps(data))


def K8s_View(request):
    data = K8s.objects.filter(deleted_by__id__isnull=True)
    dataCount = data.count()
    pageIndex = request.GET.get("pageIndex")
    pageSize = request.GET.get("pageSize")

    li_st = []
    res = []
    for item in data:
        c = open(str(item.ca)).read()
        ca = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, c)
        notafter = datetime.strptime(ca.get_notAfter().decode()[0:-1], '%Y%m%d%H%M%S')
        remain_days = notafter - datetime.now()
        di_ct = {'id': item.id, 'name': item.name, 'hostname': item.hostname.hostname, 'ca': str(item.ca),
                 'config': str(item.config), "notafter": str(notafter), "days": remain_days.days, 'desc': item.desc}

        li_st.append(di_ct)

    pageInator = Paginator(li_st, pageSize)
    context = pageInator.page(pageIndex)
    for item in context:
        res.append(item)
    data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
    return HttpResponse(json.dumps(data))


def edit_k8s(request):
    user = user_get(request)
    request_data = QueryDict(request.body)
    d_id = request_data.get("id", None)
    if request.method == "GET":
        d_id = request.GET.get("id", None)
        if d_id:
            data = K8s.objects.get(id=d_id)
        else:
            data = ""
        return render(request, "k8s/edit_k8s.html", {"data": data})

    elif request.method == "POST":
        data = {
            "name": request_data.get('name'),
            "ca": request_data.get('ca'),
            "config": request_data.get("config"),
            "desc": request_data.get('desc'),
        }
        hostname = Host.objects.get(hostname=request_data.get('hostname'), deleted_by__id__isnull=True)
        if d_id:
            K8s.objects.filter(id=d_id).update(hostname=hostname, **data)
            data = {"code": 0, "msg": "修改成功~"}
        else:
            if K8s.objects.filter(hostname=hostname, deleted_by__id__isnull=True).exists():
                data = {"code": 1, "msg": "添加失败,主机已存在~"}
            else:
                K8s.objects.create(created_by=user, hostname=hostname, **data)
                data = {"code": 0, "msg": "主机添加成功~"}
        return JsonResponse(data)

    elif request.method == "DELETE":
        K8s.objects.filter(id__in=d_id.split(",")).update(deleted_at=human_datetime(), deleted_by=user)
        data = {"code": 0, "msg": "删除成功."}
        return JsonResponse(data)


def add_ca(request):
    if request.method == 'POST':
        ca = request.FILES.get("file")
        random_str = hashlib.md5(str(random.random()).encode()).hexdigest()
        file_path = os.path.join('media/ca/', random_str + '.crt')
        try:
            with open(file_path, 'w', encoding='utf8') as f:
                data = ca.read().decode()  # bytes转str
                f.write(data)
            data = {"code": 0, "msg": "上传成功", "data": file_path}
        except Exception:
            data = {"code": 1, "msg": "上传失败"}
        return JsonResponse(data)


def add_config(request):
    if request.method == 'POST':
        config = request.FILES.get("file")
        random_str = hashlib.md5(str(random.random()).encode()).hexdigest()
        file_path = os.path.join('media/config/', random_str)
        try:
            with open(file_path, 'w', encoding='utf8') as f:
                data = config.read().decode()  # bytes转str
                f.write(data)
            data = {"code": 0, "msg": "上传成功", "data": file_path}
        except Exception:
            data = {"code": 1, "msg": "上传失败"}
        return JsonResponse(data)


def get_k8s(request):
    if request.method == "GET":
        try:
            user = user_get(request)
            hostname = request.GET.get('hostname')
            user = User.objects.get(username=user)
            host = []
            if user.is_superuser:
                data = K8s.objects.all()
                for item in data:
                    dict = {}
                    dict['hostname'] = item.hostname.hostname
                    host.append(dict)
                if hostname == "null":
                    hostname = host[0]["hostname"]
                auth_config(user, hostname)
            else:
                data = Auth.objects.filter(user_id=user.id)
                for auth in data:
                    dict = {}
                    dict['hostname'] = auth.hostname.hostname.hostname
                    host.append(dict)
                if hostname == "null":
                    hostname = host[0]["hostname"]
                auth_config(user, hostname)
            core_api = client.CoreV1Api()
            namespace = []
            for ns in core_api.list_namespace().items:
                dict = {}
                dict["name"] = ns.metadata.name
                namespace.append(dict)
            data = {"code": 0, "msg": "ok", "hostname": host, "namespace": namespace}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def rcmd(type, hostname, list, user, username, passwd=None, port=22, commands=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=passwd, port=port)
    stdin, stdout, stderr = ssh.exec_command(commands)
    out = stdout.read()
    err = stderr.read()
    dict = {}
    dict['user'] = user
    dict["hostname"] = hostname
    if type == "add":
        if out:
            user = User.objects.get(username=user)
            hostname = K8s.objects.get(hostname__hostname=hostname)
            Auth.objects.create(user=user, hostname=hostname, token=(out.decode()).replace('\n', '').replace('\r', ''))
            dict["data"] = "创建成功"
        if err:
            dict["data"] = "创建失败"
    if type == "del":
        dict["data"] = "删除成功"
        if err:
            dict["data"] = "删除失败"
    list.append(dict)


def add_auth(request):
    if request.method == "GET":
        return render(request, "k8s/add_auth.html")
    elif request.method == "POST":
        username = request.POST.get("username").split(',')
        hostname = request.POST.get("hostname").split(',')
        type = "add"
        for user in username:
            for host in Host.objects.filter(hostname__in=hostname):
                auth = Auth.objects.filter(user__username=user, hostname__hostname=host).count()
                list = []
                if auth == 0:
                    exec = open("apps/k8s/1.sh").read()
                    exec = exec.replace("username", user.lower())
                    t = threading.Thread(target=rcmd, args=(type, host.hostname, list, user),
                                         kwargs={'username': host.username, 'port': host.port,
                                                 'passwd': host.pkey, 'commands': exec, })
                    t.start()
                    t.join()
        data = {'code': 0, 'msg': "创建成功", "data": list}
        return JsonResponse(data)
    elif request.method == "DEL":
        type = "del"
        request_data = QueryDict(request.body)
        id = request_data.get("id")
        list = []
        auth = Auth.objects.get(id=id)
        user = auth.user.username
        hostname = auth.hostname.hostname
        exec = f"kubectl delete clusterrolebinding dashboard-{user.lower()} 2>&1 > /dev/null \n" \
               f"kubectl delete serviceaccount dashboard-{user.lower()} -n kube-system 2>&1 > /dev/null \n"
        t = threading.Thread(target=rcmd, args=(type, hostname.hostname, list, user),
                             kwargs={'username': hostname.username, 'port': hostname.port,
                                     'passwd': hostname.pkey, 'commands': exec, })
        t.start()
        t.join()
        for i in list:
            if "删除成功" in i["data"]:
                Auth.objects.filter(id=id).delete()
                data = {"code": 0, "msg": "删除成功."}
            else:
                data = {"code": 1, "msg": "删除失败."}
        return JsonResponse(data)


def edit_auth(request):
    if request.method == "GET":
        id = request.GET.get("id")
        data = Auth.objects.get(id=id)
        dict = {}
        dict["id"] = data.id
        dict["username"] = data.user.username
        dict["hostname"] = data.hostname.hostname.hostname
        dict["token"] = data.token
        return render(request, "k8s/edit_auth.html", dict)
    if request.method == "POST":
        edit_id = request.POST.get("id")
        username = request.POST.get("username")
        hostname = request.POST.get("hostname")
        token = request.POST.get("token")

        username = User.objects.get(username=username)
        hostname = K8s.objects.get(hostname__hostname=hostname)

        obj = Auth.objects.get(id=edit_id)
        obj.user = username
        obj.hostname = hostname
        obj.token = token
        obj.save()
        data = {"code": 0, "msg": "修改成功~"}
        return JsonResponse(data)
