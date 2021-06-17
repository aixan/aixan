from django.views.generic import View
from apps.lib.mixins import json_response
from apps.lib.parser import JsonParser, Argument
from apps.lib.channel import Channel
from apps.exec.models import Exec
from apps.host.models import Host
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
import json
from apps.exec.executors import dispatch
from apps.exec.models import Exec, Schedule, History
from django_redis import get_redis_connection
from django.conf import settings
from apps.lib.set import user_get
from apps.lib.utils import human_datetime
import threading
import paramiko
from apps.exec.forms import Template


def task(request):
    if request.method == "GET":
        return render(request, "exec/task.html")


def template(request):
    if request.method == "GET":
        data = Exec.objects.all()
        li_st = []
        for item in data:
            li_st.append(item.types)
        return render(request, "exec/template.html", {"types": list(set(li_st))})


def template_type(request):
    request_data = QueryDict(request.body)
    name = request_data.get("name", None)
    types = request_data.get("types", None)
    if request.method == "GET":
        data = Exec.objects.filter(deleted_by__id__isnull=True)
        li_st = []
        for item in data:
            li_st.append(item.types)
        data = {"code": 0, "msg": "获取成功", "data": list(set(li_st))}
        return JsonResponse(data)
    elif request.method == "POST":
        if Exec.objects.filter(types=types, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "类别存在，添加失败~"}
        else:
            data = {"code": 0, "msg": "添加成功~"}
        return JsonResponse(data)

    elif request.method == "PUT":
        if Exec.objects.filter(types=types, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "类别存在，修改失败~"}
        else:
            Exec.objects.filter(types=name, deleted_by__id__isnull=True).update(types=types)
            data = {"code": 0, "msg": "修改成功~"}
        return JsonResponse(data)


def template_edit(request):
    request_data = QueryDict(request.body)
    user = user_get(request)
    did = request_data.get("id", None)
    if request.method == "GET":
        did = request.GET.get("id", None)
        if did:
            data = Exec.objects.get(id=did)
        else:
            data = ""
        return render(request, "exec/template_edit.html", {"data": data})
    if request.method == "POST":
        data = {
            "name": request_data.get('name'),
            "types": request_data.get('types'),
            "body": request_data.get('body'),
            "desc": request_data.get('desc'),
        }
        if did:
            Exec.objects.filter(id=did).update(**data)
            data = {"code": 0, "msg": "模板修改成功。"}
        else:
            Exec.objects.create(created_by=user, **data)
            data = {"code": 0, "msg": "添加模板成功。"}
        return JsonResponse(data)

    elif request.method == "DELETE":
        Exec.objects.filter(id__in=did.split(',')).update(deleted_at=human_datetime(), deleted_by=user)
        data = {"code": 0, "msg": "模板删除成功~"}
        return JsonResponse(data)


def template_get(request):
    data = Exec.objects.all()
    dataCount = data.count()
    pageIndex = request.GET.get("pageIndex")
    pageSize = request.GET.get("pageSize")

    li_st = []
    res = []
    for item in data:
        di_ct = {'id': item.id, 'name': item.name, 'types': item.types, 'body': item.body, 'desc': item.desc}
        li_st.append(di_ct)
    pageInator = Paginator(li_st, pageSize)
    context = pageInator.page(pageIndex)
    for item in context:
        res.append(item)
    data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
    return HttpResponse(json.dumps(data))


def template_search(request):
    types = request.GET.get("types")
    name = request.GET.get("name")
    body = request.GET.get("body")

    data = Exec.objects.filter(types__contains=types, name__contains=name, body__contains=body,
                               deleted_by__id__isnull=True)
    li_st = []
    for item in data:
        di_ct = {'id': item.id, 'types': item.types, 'name': item.name, 'body': item.body, 'desc': item.desc}
        li_st.append(di_ct)

    data = {"code": 0, "msg": "ok", "DataCount": 1, "data": li_st}
    return HttpResponse(json.dumps(data))


def schedule(request):
    if request.method == "GET":
        return render(request, "exec/schedule.html")


def schedule_type(request):
    request_data = QueryDict(request.body)
    name = request_data.get("name")
    types = request_data.get("types")
    if request.method == "GET":
        data = Schedule.objects.filter(deleted_by__id__isnull=True)
        li_st = []
        for item in data:
            li_st.append(item.types)
        data = {"code": 0, "msg": "获取成功", "data": list(set(li_st))}
        return JsonResponse(data)
    elif request.method == "POST":
        if Schedule.objects.filter(types=types, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "类别存在，添加失败~"}
        else:
            data = {"code": 0, "msg": "添加成功~"}
        return JsonResponse(data)

    elif request.method == "PUT":
        if Schedule.objects.filter(types=types, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "类别存在,修改失败~"}
        else:
            Schedule.objects.filter(types=name, deleted_by__id__isnull=True).update(types=types)
            data = {"code": 0, "msg": "修改成功~"}
        return JsonResponse(data)


def schedule_edit(request):
    user = user_get(request)
    request_data = QueryDict(request.body)
    did = request_data.get("id", None)
    if request.method == "GET":
        did = request.GET.get("id")
        if did:
            data = Schedule.objects.get(id=did)
            data.targets = ','.join(eval(data.targets))
            data.rst_notify = eval(data.rst_notify)
        else:
            data = ""
        return render(request, "exec/schedule_edit.html", {"data": data})
    elif request.method == "POST":
        data = {
            'name': request.POST.get("name"),
            'types': request.POST.get("types"),
            'command': request.POST.get("command"),
            'targets': request.POST.get("targets").split(","),
            'desc': request.POST.get("desc"),
            'rst_notify': {"mode": request_data.get('rst_notify.mode'), 'value': request_data.get('rst_notify.value')}
        }
        trigger = request.POST.get("trigger")
        if did:
            if trigger == "interval":
                interval = request.POST.get("interval")
                Schedule.objects.filter(id=did).update(trigger=trigger, trigger_args=interval, **data)
            elif trigger == "date":
                date = request.POST.get("date")
                Schedule.objects.filter(id=did).update(trigger=trigger, trigger_args=date, **data)
            elif trigger == "cron":
                cron = request.POST.get("cron")
                Schedule.objects.filter(id=did).update(trigger=trigger, trigger_args=cron, **data)
            obj = Schedule.objects.filter(id=did).first()
            if obj and obj.is_active:
                message = {'id': obj.id, 'action': 'modify'}
                message.update({'trigger': obj.trigger, 'trigger_args': obj.trigger_args, 'command': obj.command,
                                'targets': obj.targets})
                rds_cli = get_redis_connection()
                rds_cli.lpush(settings.SCHEDULE_KEY, json.dumps(message))
            data = {"code": 0, "msg": "类别修改成功~"}
        else:
            if trigger == "interval":
                interval = request.POST.get("interval")
                Schedule.objects.create(created_by=user, trigger=trigger, trigger_args=interval, **data)
            elif trigger == "date":
                date = request.POST.get("date")
                Schedule.objects.create(created_by=user, trigger=trigger, trigger_args=date, **data)
            elif trigger == "cron":
                cron = request.POST.get("cron")
                Schedule.objects.create(created_by=user, trigger=trigger, trigger_args=cron, **data)
            data = {"code": 0, "msg": "任务添加成功~"}
        return JsonResponse(data)

    elif request.method == "DELETE":
        obj = Schedule.objects.filter(id=did).first()
        if obj:
            if obj.is_active:
                data = {"code": 1, "msg": "该任务在运行中，请先停止任务再尝试删除"}
            else:
                Schedule.objects.filter(id=did).update(deleted_at=human_datetime(), deleted_by=user)
                data = {"code": 0, "msg": "任务删除成功"}
            return JsonResponse(data)
    elif request.method == "PUT":
        obj = Schedule.objects.filter(id=did).first()
        if obj:
            if obj.is_active:
                obj.is_active = 0
                obj.save()
                message = {'id': did, 'action': 'remove'}
                data = {"code": 1, "msg": "任务已停止"}
            else:
                message = {'id': did, 'action': 'add'}
                message.update({'trigger': obj.trigger, 'trigger_args': obj.trigger_args, 'command': obj.command,
                                'targets': obj.targets})
                obj.is_active = 1
                obj.save()
                data = {"code": 0, "msg": "任务启动成功"}
            rds_cli = get_redis_connection()
            rds_cli.lpush(settings.SCHEDULE_KEY, json.dumps(message))
            return JsonResponse(data)


def schedule_view(request):
    if request.method == "GET":
        did = request.GET.get("id", None)
        hid = request.GET.get("hid", None)
        if did:
            data = Schedule.objects.get(id=did)
            data = data.latest.id
        if hid:
            data = hid
        record = History.objects.filter(id=data).first()
        outputs = json.loads(record.output)
        host_ids = (x[0] for x in outputs if isinstance(x[0], int))
        hosts_info = {x.id: x.hostname for x in Host.objects.filter(id__in=host_ids, deleted_by__id__isnull=True)}
        data = {'run_time': record.run_time, 'success': 0, 'failure': 0, 'duration': 0, 'outputs': []}
        for h_id, code, duration, out in outputs:
            key = 'success' if code == 0 else 'failure'
            data[key] += 1
            data['duration'] += duration
            data['outputs'].append({
                'name': hosts_info.get(h_id, '本机'),
                'code': code,
                'duration': duration,
                'output': out})
        data['duration'] = f"{data['duration'] / len(outputs):.3f}"
        return render(request, "exec/schedule_view.html", data)
    elif request.method == "POST":
        did = request.POST.get("id")
        data = Schedule.objects.filter(id=did).first()
        if not data:
            data = {"code": 1, "msg": "未找到指定任务"}
            return JsonResponse(data)
        data = dispatch(data.command, eval(data.targets), True)
        score = 0
        for item in data:
            score += 1 if item[1] else 0
        history = History.objects.create(
            task_id=did,
            status=2 if score == len(data) else 1 if score else 0,
            run_time=human_datetime(),
            output=json.dumps(data)
        )
        data = {"code": 0, "msg": "执行成功", "data": history.id}
        return JsonResponse(data)


def schedule_get(request):
    if request.method == "GET":
        data = Schedule.objects.filter(deleted_by__id__isnull=True)
        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        li_st = []
        res = []
        for item in data:
            if item.latest:
                latest = item.latest.status
                hid = item.latest_id
                rtime = item.latest.run_time
            else:
                latest = ""
                rtime = ""
                hid = ""
            di_ct = {'id': item.id, 'name': item.name, 'types': item.types, 'command': item.command, 'desc': item.desc,
                     "is_active": item.is_active, "status": latest, "rtime": rtime, "hid": hid}
            li_st.append(di_ct)
        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))


def schedule_history(request):
    if request.method == "GET":
        return render(request, "exec/schedule_history.html")


def schedule_hist(request):
    if request.method == "GET":
        did = request.GET.get("id")
        data = History.objects.filter(task_id=did)
        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        li_st = []
        res = []
        for item in data:
            di_ct = {'id': item.id, 'status': item.status, 'run_time': item.run_time}
            li_st.append(di_ct)
        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))
