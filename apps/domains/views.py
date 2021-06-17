from django.shortcuts import render
from apps.domains.models import Api, Domains, Parsing, Ca
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse, QueryDict
import json
from apps.lib.utils import human_datetime
from apps.lib.set import user_get
from apps.lib.aliyun import Ali_Domain, Ali_Add_Domain, \
    Ali_Parsing, Ali_Del_Parsing, Ali_Get_Parsing, Ali_Edit_Parsing
import requests


def api(request):
    if request.method == "GET":
        return render(request, "domains/api.html")


def api_edit(request):
    request_data = QueryDict(request.body)
    did = request_data.get("id", None)
    user = user_get(request)
    if request.method == "GET":
        did = request.GET.get('id')
        if did:
            data = Api.objects.get(id=did)
        else:
            data = ""
        return render(request, "domains/api_edit.html", {"data": data})

    elif request.method == "POST":
        data = {
            "name": request_data.get("name"),
            "cloud": request_data.get("cloud"),
            "region": request_data.get("region"),
            "key": request_data.get("key"),
            "secret": request_data.get("secret"),
            "desc": request_data.get("desc"),
        }
        api_key = Ali_Domain(data["key"], data["secret"], data["region"])
        if api_key['code'] == 0:
            if did:
                Api.objects.filter(id=did).update(**data)
                data = {"code": 0, "msg": "API修改成功~"}
            else:
                Api.objects.create(created_by=user, **data)
                data = {"code": 0, "msg": "API添加成功~"}
        else:
            data = {"code": 0, "msg": "API接口验证失败~"}
        return JsonResponse(data)

    elif request.method == "DELETE":
        Api.objects.filter(id__in=did.split(',')).update(deleted_at=human_datetime(), deleted_by=user)
        data = {"code": 0, "msg": "API删除成功~"}
        return JsonResponse(data)

    elif request.method == "PUT":
        if did:
            Api_obj = Api.objects.filter(id__in=did)
        else:
            Api_obj = Api.objects.all()
        if Api_obj.count() < 0:
            data = {"code": 1, "msg": f"请添加API接口"}
        else:
            li_st = []
            cg, sb = 0, 0
            for item in Api_obj:
                data = Ali_Domain(item.key, item.secret, item.region)
                if data['code'] == 0:
                    data = json.loads(data['data'])
                    for i in data['Domains']['Domain']:
                        di_ct = {'api_id': item.id, 'domain': i['DomainName'], 'dns1': i['DnsServers']['DnsServer'][0],
                                 'dns2': i['DnsServers']['DnsServer'][1]}
                        Domains.objects.update_or_create(domain=i['DomainName'], defaults=di_ct, created_by=user)
                    cg += 1
                else:
                    li_st.append(item.name)
                    sb += 1
            if sb > 1:
                data = {"code": 1, "msg": f"同步异常，总:{Api_obj.count()},成功:{cg},失败:{sb},失败名称{str(li_st)}"}
            else:
                data = {"code": 0, "msg": f"同步成功，总:{Api_obj.count()},成功:{cg},失败:{sb}"}
        return JsonResponse(data)


def api_get(request):
    if request.method == "GET":
        data = Api.objects.filter(deleted_by__id__isnull=True)
        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        li_st = []
        res = []
        for item in data:
            if item.cloud == "1":
                data = Ali_Domain(item.key, item.secret, item.region)
            di_ct = {'id': item.id, 'name': item.name, 'cloud': item.cloud, 'region': item.region, "desc": item.desc,
                     'status': data['code']}
            li_st.append(di_ct)

        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))


def domains(request):
    user = user_get(request)
    if request.method == "GET":
        data = Domains.objects.filter(deleted_by__id__isnull=True)
        data = {"data": data}
        return render(request, "domains/domains.html", data)
    elif request.method == "SYNC":
        request_data = QueryDict(request.body)
        id = request_data.get("id")
        domain = Domains.objects.get(id=id)
        data = Ali_Parsing(domain.api.key, domain.api.secret, domain.api.region, domain.domain)
        if data['code'] == 0:
            data = json.loads(data['data'])
            for item in data['DomainRecords']['Record']:
                dict = {}
                dict['RR'] = item['RR']
                dict['Line'] = item['Line']
                dict['Type'] = item['Type']
                dict['Value'] = item['Value']
                dict['RecordId'] = item['RecordId']
                dict['TTL'] = item['TTL']
                dict['domain_id'] = domain.id
                if "Priority" in item:
                    dict['Priority'] = item['Priority']
                else:
                    dict['Priority'] = None
                Parsing.objects.update_or_create(RecordId=item['RecordId'], defaults=dict, created_by=user)
            data = {"code": 0, "msg": "域名解析同步成功~"}
        else:
            data = {"code": 1, "msg": "域名解析同步失败~"}
        return JsonResponse(data)


def domains_add(request):
    request_data = QueryDict(request.body)
    did = request_data.get("id", None)
    user = user_get(request)
    if request.method == "GET":
        data = Api.objects.filter().values('id', 'name')
        return render(request, "domains/domains_add.html", {'api': data})
    if request.method == "POST":
        id = request.POST.get("id")
        domain = request.POST.get("domain")
        obj = Domains.objects.filter(domain=domain)
        if obj.count() == 0:
            api = Api.objects.get(id=id)
            data = Ali_Add_Domain(api.key, api.secret, api.region, domain)
            if data['code'] == 0:
                data = json.loads(data['data'])
                dns1 = data['DnsServers']['DnsServer'][0]
                dns2 = data['DnsServers']['DnsServer'][1]
                Domains.objects.create(api=api, domain=domain, dns1=dns1, dns2=dns2)
            data = {"code": 0, "msg": "添加域名成功~"}
        else:
            data = {"code": 1, "msg": "添加域名失败~"}
        return JsonResponse(data)
    elif request.method == "DELETE":
        id = request.POST.get('id')
        Domains.objects.get(id=id).delete()
        data = {"code": 0, "msg": "域名删除成功~"}
        return JsonResponse(data)


def parsing_get(request):
    if request.method == "GET":
        did = request.GET.get("id", None)
        if did:
            data = Parsing.objects.filter(domain_id=did, deleted_by__id__isnull=True)
        else:
            data = Parsing.objects.filter(deleted_by__id__isnull=True)
        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        li_st = []
        res = []
        for item in data:

            dict = {'id': item.id, 'RR': item.RR, 'Type': item.Type, 'Line': item.Line, 'TTL': item.TTL,
                    "domain": item.domain.domain}
            if item.Priority:
                dict['Value'] = "{} | {}".format(item.Value, item.Priority)
            else:
                dict['Value'] = item.Value
            data = Ali_Get_Parsing(item.domain.api.key, item.domain.api.secret, item.domain.api.region, item.RecordId)
            if data['code'] == 0:
                data = json.loads(data['data'])
                if len(data) > 1 and data['Status'] == "ENABLE":
                    dict['status'] = 0
                else:
                    dict['status'] = 1
            else:
                dict['status'] = 1
            li_st.append(dict)

        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))


def parsing_edit(request):
    request_data = QueryDict(request.body)
    user = user_get(request)
    did = request_data.get("id", None)
    if request.method == "GET":
        dom = Domains.objects.filter(deleted_by__id__isnull=True)
        did = request.GET.get('id', None)
        if did:
            data = Parsing.objects.get(id=did)
        else:
            data = ""
        return render(request, "domains/parsing_edit.html", {"data": data, "domain": dom})
    elif request.method == "POST":
        data = {
            "RR": request_data.get("RR"),
            "Type": request_data.get("Type"),
            "Value": request_data.get("Value"),
            "TTL": request_data.get("TTL"),
            "Line": request_data.get("Line"),
            "Priority": request_data.get("Priority", None),
            "RecordId": request_data.get("RecordId", None),
        }
        pars = Domains.objects.get(id=request_data.get("domain"))
        if did:
            api_key = Ali_Edit_Parsing(pars.api.key, pars.api.secret, pars.api.region, **data)
            if api_key['code'] == 0:
                Parsing.objects.filter(id=did).update(**data)
                data = {"code": 0, "msg": "域名解析修改成功~"}
            else:
                data = {"code": 0, "msg": "域名解析失败~"}
        else:
            api_key = Ali_Edit_Parsing(pars.api.key, pars.api.secret, pars.api.region, pars.domain, **data)
            if api_key['code'] == 0:
                data['RecordId'] = json.loads(api_key['data'])['RecordId']
                Parsing.objects.create(created_by=user, **data, domain=pars)
                data = {"code": 0, "msg": "域名解析添加成功~"}
            else:
                data = {"code": 0, "msg": "域名解析失败~"}
        return JsonResponse(data)
    elif request.method == "DELETE":
        Pars = Parsing.objects.filter(id=did)
        data = Ali_Del_Parsing(Pars.first().domain.api.key, Pars.first().domain.api.secret,
                               Pars.first().domain.api.region, Pars.first().RecordId)
        if data['code'] == 0:
            Pars.update(deleted_at=human_datetime(), deleted_by=user)
            data = {"code": 0, "msg": "域名解析同步删除成功~"}
        else:
            Pars.update(deleted_at=human_datetime(), deleted_by=user)
            data = {"code": 0, "msg": "域名解析本地删除成功~"}
        return JsonResponse(data)
    elif request.method == "SYNC":
        domain = Domains.objects.filter(deleted_by__id__isnull=True)
        if domain:
            for item in domain:
                api_key = Ali_Parsing(item.api.key, item.api.secret, item.api.region, item.domain)
                if api_key['code'] == 0:
                    data = json.loads(api_key['data'])
                    for dom in data['DomainRecords']['Record']:
                        if "Priority" in dom:
                            Priority = dom['Priority']
                        else:
                            Priority = None
                        di_ct = {'RR': dom['RR'], 'Line': dom['Line'], 'Type': dom['Type'], 'Value': dom['Value'],
                                 'RecordId': dom['RecordId'], 'TTL': dom['TTL'], 'domain_id': item.id,
                                 'Priority': Priority}
                        Parsing.objects.update_or_create(RecordId=dom['RecordId'], defaults=di_ct, created_by=user)
                else:
                    pass
            data = {"code": 0, "msg": "域名解析同步成功~"}
        else:
            data = {"code": 1, "msg": "域名查找失败~"}
        return JsonResponse(data)


def ca(request):
    if request.method == "GET":
        return render(request, "domains/ca.html")


def get_ca(request):
    if request.method == "GET":
        data = Ca.objects.all()
        dataCount = data.count()
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        li_st = []
        res = []
        for item in data:
            di_ct = {'id': item.id, 'domain': item.domain, 'etime': item.etime}
            li_st.append(di_ct)

        pageInator = Paginator(li_st, pageSize)
        context = pageInator.page(pageIndex)
        for item in context:
            res.append(item)
        data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
        return HttpResponse(json.dumps(data))
