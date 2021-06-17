from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Heartbeat, Alarm
import json
import time
import datetime


def data():
    xtime = Heartbeat.objects.first()
    context = {'heartbeat': xtime}
    return context


def alarm(request):
    context = data()
    category_list = ['故障', '已恢复']
    context['category_list'] = category_list
    return render(request, "info/alarm.html", context)


def get_page(request):
    data = Alarm.objects.all()
    dataCount = data.count()
    pageIndex = request.GET.get("pageIndex")
    pageSize = request.GET.get("pageSize")

    list = []
    res = []
    for item in data:
        dict = {}
        dict['id'] = item.id
        dict['state'] = item.state
        dict['IP'] = item.IP
        dict['problem'] = item.problem
        dict['why'] = item.why
        dict['e_time'] = item.e_time
        data_f_time = item.f_time.strftime("%Y-%m-%d %H:%M:%S")
        dict['f_time'] = data_f_time
        data_r_time = str(item.r_time)
        dict['r_time'] = data_r_time
        dict['e_id'] = item.e_id
        list.append(dict)
    pageInator = Paginator(list, pageSize)
    context = pageInator.page(pageIndex)
    for item in context:
        res.append(item)
    data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
    return HttpResponse(json.dumps(data))


def search_page(request):
    ip = request.GET.get("IP", None)
    state = request.GET.get("state", None)
    problem = request.GET.get("problem", None)
    f_time = request.GET.get("f_time", None)

    data = Alarm.objects.filter(
        IP__contains=ip,
        state__contains=state,
        problem__contains=problem,
        f_time__contains=f_time
    )

    list = []
    for item in data:
        dict = {}
        dict['id'] = item.id
        dict['state'] = item.state
        dict['IP'] = item.IP
        dict['problem'] = item.problem
        dict['why'] = item.why
        dict['e_time'] = item.e_time
        data_f_time = item.f_time.strftime("%Y-%m-%d %H:%M:%S")
        dict['f_time'] = data_f_time
        data_r_time = str(item.r_time)
        dict['r_time'] = data_r_time
        dict['e_id'] = item.e_id
        list.append(dict)

    data = {"code": 0, "msg": "ok", "DataCount": 1, "data": list}
    return HttpResponse(json.dumps(data))


def delete_page(request):
    get_id = request.GET.get("id")
    Alarm.objects.filter(id=get_id).delete()
    return render(request, "info/alarm.html")


def update_page(request):
    get_id = request.GET.get("id")
    get_state = request.GET.get("state")
    get_e_time = request.GET.get("e_time")
    get_r_time = request.GET.get("r_time")

    obj = Alarm.objects.get(id=get_id)
    obj.state = get_state
    obj.e_time = get_e_time
    obj.r_time = get_r_time
    obj.save()
    return render(request, "info/alarm.html")
