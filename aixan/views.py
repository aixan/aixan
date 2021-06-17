from django.shortcuts import render, HttpResponse
from apps.info.models import Heartbeat, Alarm
from apps.host.models import Host
from apps.user.models import User
from django.http import JsonResponse
import time
import datetime
from kubernetes import client, config


def data():
    xtime = Heartbeat.objects.first()
    gz = Alarm.objects.values("IP").annotate()
    today = datetime.datetime.now().date()
    atoday = (Alarm.objects.filter(f_time__gte=str(today), state="故障")).count()
    atodayz = (Alarm.objects.filter(f_time__gte=str(today))).count()
    atodayr = (Alarm.objects.filter(f_time__gte=str(today), state="已恢复")).count()
    alarmm = (Alarm.objects.filter(f_time__month=today.month, state="故障")).count()
    alarmmh = (Alarm.objects.filter(f_time__month=today.month, state="已恢复")).count()
    alarmmz = (Alarm.objects.filter(f_time__month=today.month)).count()
    alarm = (Alarm.objects.filter(state="故障")).count()
    alarmh = (Alarm.objects.filter(state="已恢复")).count()
    alarmz = (Alarm.objects.all()).count()
    host = Host.objects.all().count()
    context = {
        'heartbeat': xtime,  # .time.strftime("%m-%d %H:%M"),
        'atoday': atoday,
        'atodayr': atodayr,
        'atodayz': atodayz,
        'alarmm': alarmm,
        'alarmmh': alarmmh,
        'alarmmz': alarmmz,
        'alarm': alarm,
        'alarmh': alarmh,
        'alarmz': alarmz,
        'host': host,
    }
    category_list = ['所有内容', '故障', '已恢复']
    context['category_list'] = category_list
    return context


def index(request):
    context = data()
    return render(request, "index.html", context)


def home(request):
    context = data()
    return render(request, "home.html", context)


def kubernetes(request):
    return render(request, 'kubernetes.html')


def setting(request):
    context = {}
    return render(request, "setting.html", context)
