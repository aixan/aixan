from django.shortcuts import render
from apps.alarm.models import Contact, Group, Alarm
from apps.lib.utils import human_datetime
from apps.lib.set import user_get
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse, QueryDict
import json


def contact(request):
    if request.method == "GET":
        return render(request, "alarm/contact.html")


def contact_get(request):
    if request.method == "GET":
        data = Contact.objects.filter(deleted_by__id__isnull=True)
        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        li_st = []
        res = []
        for item in data:
            di_ct = {'id': item.id, 'name': item.name, 'phone': item.phone, 'email': item.email, 'ding': item.ding,
                     'wx_token': item.wx_token, 'qy_wx': item.qy_wx}
            li_st.append(di_ct)
        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))


def contact_edit(request):
    request_data = QueryDict(request.body)
    did = request_data.get('id', None)
    user = user_get(request)
    if request.method == "GET":
        did = request.GET.get('id')
        if did:
            data = Contact.objects.filter(id=did).first()
        else:
            data = ""
        return render(request, "alarm/contact_edit.html", {"data": data})
    elif request.method == "POST":
        data = {
            "name": request_data.get("name"),
            "phone": request_data.get("phone"),
            "email": request_data.get("email"),
            "ding": request_data.get("ding"),
            "wx_token": request_data.get("wx_token"),
            "qy_wx": request_data.get("qy_wx"),
        }
        if did:
            Contact.objects.filter(id=did).update(**data)
            data = {"code": 1, "msg": "联系人修改成功~"}
        else:
            Contact.objects.create(created_by=user, **data)
            data = {"code": 0, "msg": "联系人添加成功~"}
        return JsonResponse(data)

    elif request.method == "DELETE":
        Contact.objects.filter(id__in=did.split(',')).update(deleted_at=human_datetime(), deleted_by=user)
        data = {"code": 0, "msg": "联系人删除成功"}
        return JsonResponse(data)


def group(request):
    return render(request, "alarm/group.html")


def group_get(request):
    if request.method == "GET":
        data = Group.objects.filter(deleted_by__id__isnull=True)

        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")
        li_st = []
        res = []
        for item in data:
            contact = []
            for i in data.filter(id=item.id).values("contacts__name"):
                contact.append(i['contacts__name'])
            print(len(contact))
            if len(contact) >= 1 and contact[0] != None:
                contact = ' | '.join(contact)
            else:
                contact = ""
            di_ct = {'id': item.id, 'name': item.name, 'desc': item.desc, "contact": contact}

            li_st.append(di_ct)
        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))


def group_edit(request):
    request_data = QueryDict(request.body)
    did = request_data.get('id', None)
    user = user_get(request)
    if request.method == "GET":
        did = request.GET.get("id")
        data = Contact.objects.filter(deleted_by__id__isnull=True)
        if data:
            li_st = []
            for item in data:
                di_ct = {"value": item.id, "title": item.name}
                li_st.append(di_ct)
        else:
            li_st = ""
        if did:
            data = Group.objects.filter(id=did).first()
            value = []
            for item in data.contacts.all():
                value.append(item.id)
            data.contact = li_st
            data.values = value
        else:
            data = {"contact": li_st, "values": ""}
        return render(request, "alarm/group_edit.html", {"data": data})
    if request.method == "POST":
        data = {
            "name": request_data.get("name"),
            "desc": request_data.get("desc"),
        }
        contacts = json.loads(request_data.get("contacts"))
        li_st = []
        for item in contacts:
            li_st.append(int(item['value']))
        print(li_st)
        if did:
            contacts = Contact.objects.filter(id__in=li_st)
            print(contacts)
            data = Group.objects.filter(id=did)
            data.contacts.add(*li_st)
            data.update(**data)
            data.save()
            print(data, "1")
            # data.contacts.add(*contacts)
            # data.save()
            data = {"code": 0, "msg": "联系组修改成功~"}
        else:
            data = Group.objects.create(created_by=user, **data)
            data.contacts.add(*contacts)
            data = {"code": 0, "msg": "联系组添加失败~"}
        return JsonResponse(data)


def alarm(request):
    return render(request, "alarm/alarm.html")


def alarm_get(request):
    if request.method == "GET":
        data = Alarm.objects.all()

        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        li_st = []
        res = []
        for item in data:
            di_ct = {'id': item.id, 'name': item.name, 'type': item.type, 'status': item.status,
                     'duration': item.duration, 'notify_mode': item.notify_mode, 'notify_grp': item.notify_grp,
                     'created_at': item.created_at}
            li_st.append(di_ct)
        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))
