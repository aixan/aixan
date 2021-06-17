from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
from apps.host.models import Host
from apps.setting.utils import AppSetting
from apps.lib.utils import human_datetime
from apps.lib.exec import SSH, AuthenticationException
from paramiko.ssh_exception import BadAuthenticationType
from apps.user.models import User
from apps.lib.set import user_get
import json


def host(request):
    if request.method == "GET":
        data = Host.objects.all()
        types, system = [], []
        for item in data:
            types.append(item.types)
            system.append(item.system)
        context = {"types": list(set(types)), "system": list(set(system))}
        return render(request, "host/host.html", context)
    elif request.method == "DELETE":
        user = user_get(request)
        request_data = QueryDict(request.body)
        did = request_data.get("id").split(",")
        Host.objects.filter(id__in=did).update(deleted_at=human_datetime(), deleted_by=user)
        data = {"code": 0, "msg": "主机删除成功~"}
        return JsonResponse(data)
    elif request.method == "POST":
        key = request.FILES.get("file")
        data = key.read()
        data = {"code": 0, "msg": "上传成功", "data": data.decode('utf-8')}
        return JsonResponse(data)


def get_host(request):
    data = Host.objects.filter(deleted_by_id__isnull=True)
    dataCount = data.count()
    pageIndex = request.GET.get("pageIndex")
    pageSize = request.GET.get("pageSize")

    li_st = []
    res = []
    for item in data:
        di_ct = {'id': item.id, 'types': item.types, 'name': item.name, 'system': item.system,
                 'hostname': item.hostname,
                 'port': item.port, 'desc': item.desc}
        li_st.append(di_ct)

    pageInator = Paginator(li_st, pageSize)
    context = pageInator.page(pageIndex)
    for item in context:
        res.append(item)
    data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
    return HttpResponse(json.dumps(data))


def get_type(request):
    request_data = QueryDict(request.body)
    name = request_data.get("name", None)
    types = request_data.get("types", None)
    if request.method == "GET":
        data = Host.objects.filter(deleted_by__id__isnull=True)
        li_st = []
        for item in data:
            li_st.append(item.types)
        data = {"code": 0, "msg": "获取成功", "data": list(set(li_st))}
        return JsonResponse(data)
    elif request.method == "POST":
        if Host.objects.filter(types=types, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "类别存在，添加失败~"}
        else:
            data = {"code": 0, "msg": "添加成功"}
        return JsonResponse(data)

    elif request.method == "PUT":
        if Host.objects.filter(types=types, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "类别存在，修改失败~"}
        else:
            Host.objects.filter(types=name, deleted_by__id__isnull=True).update(types=types)
            data = {"code": 0, "msg": "修改成功~"}
        return JsonResponse(data)


def edit_host(request):
    if request.method == "GET":
        did = request.GET.get("id", None)
        if did:
            data = Host.objects.get(id=did)
        else:
            data = ""
        return render(request, "host/edit_host.html", {"host": data})
    elif request.method == "POST":
        user = user_get(request)
        did = request.POST.get("id", None)
        password = request.POST.get("password", None)
        data = {
            "types": request.POST.get("types"),
            "system": request.POST.get("system"),
            "name": request.POST.get("name"),
            "username": request.POST.get("username"),
            "hostname": request.POST.get("hostname"),
            "port": request.POST.get("port"),
            "pkey": request.POST.get("pkey"),
            "desc": request.POST.get("desc"),
        }
        valid = valid_ssh(data['hostname'], data['port'], data['username'], password=password, pkey=data['pkey'])
        if valid[0] is False:
            data = {"code": 1, "msg": valid[2]}
            return JsonResponse(data)
        if did:
            Host.objects.filter(id=did).update(**data)
            data = {"code": 0, "msg": "修改主机成功~"}
        elif Host.objects.filter(hostname=data['hostname'], deleted_by_id__isnull=True).exists():
            data = {"code": 1, "msg": "添加失败,主机已存在~"}
        else:
            Host.objects.create(created_by=user, **data)
            data = {"code": 0, "msg": "添加主机成功~"}
        return JsonResponse(data)


def search(request):
    types = request.GET.get("types")
    name = request.GET.get("name")
    system = request.GET.get("system")
    hostname = request.GET.get("hostname")

    data = Host.objects.filter(types__contains=types, name__contains=name, system__contains=system,
                               hostname__contains=hostname, deleted_by__id__isnull=True)

    li_st = []
    for item in data:
        di_ct = {'id': item.id, 'types': item.types, 'name': item.name, 'system': item.system,
                 'hostname': item.hostname,
                 'port': item.port, 'desc': item.desc}
        li_st.append(di_ct)

    data = {"code": 0, "msg": "ok", "DataCount": 1, "data": li_st}
    return HttpResponse(json.dumps(data))


def valid_ssh(hostname, port, username, password=None, pkey=None, with_expect=True):
    try:
        private_key = AppSetting.get('private_key')
        public_key = AppSetting.get('public_key')
    except KeyError:
        private_key, public_key = SSH.generate_key()
        AppSetting.set('private_key', private_key, 'ssh private key')
        AppSetting.set('public_key', public_key, 'ssh public key')
    try:
        if password:
            _cli = SSH(hostname, port, username, password=str(password))
            _cli.add_public_key(public_key)
        if pkey:
            private_key = pkey
        cli = SSH(hostname, port, username, private_key)
        cli.ping()
    except BadAuthenticationType:
        if with_expect:
            data = '该主机不支持密钥认证，错误代码：E01'
        else:
            data = '该主机不支持密钥认证，错误代码：E02'
        return False, 500, data
    except AuthenticationException:
        if password and with_expect:
            data = '密钥认证失败，错误代码：E03'
        else:
            data = "密钥认证失败，错误代码：E04"
        return False, 500, data
    return True, 200, {'msg': "认证成功"}
