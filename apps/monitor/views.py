from django.shortcuts import render
from apps.alarm.models import Contact, Group, Alarm
# Create your views here.
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
import json
from apps.monitor.models import *


def monitor(request):
    return render(request, "monitor/monitor.html")


def add_test(request):
    return render(request, "monitor/add_test.html")


def get_monitor(request):
    if request.method == "GET":
        data = MonT.objects.all()

        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        for item in data:
            dict = {}
            dict['id'] = item.id
            dict['name'] = item.name
            list.append(dict)
        pageInator = Paginator(list, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))