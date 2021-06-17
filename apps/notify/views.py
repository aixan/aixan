from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from apps.notify.models import Notify
# from libs import json_response, JsonParser, Argument
from django.http import HttpResponse, JsonResponse, QueryDict


def Notify_get(request):
    if request.method == "GET":
        notifies = Notify.objects.filter(unread=True)
        return JsonResponse(notifies)
    if request.method == "POST":
        did = request.POST.get("id")
        Notify.objects.filter(id__in=did).update(unread=False)
        data = {"code": 0, "msg": ""}
        return JsonResponse(data)
