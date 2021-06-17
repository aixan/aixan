from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeDomainsRequest import DescribeDomainsRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.AddDomainRequest import AddDomainRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteDomainRecordRequest import DeleteDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordInfoRequest import DescribeDomainRecordInfoRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
import json


def Ali_Domain(key, secret, region):
    try:
        client = AcsClient(key, secret, region)
        request = DescribeDomainsRequest()
        request.set_accept_format('json')
        response = client.do_action_with_exception(request)
        data = {"code": 0, "data": response.decode(encoding='utf-8')}
        return data
    except Exception:
        return {"code": 1}


def Ali_Parsing(key, secret, region, domain):
    try:
        client = AcsClient(key, secret, region)
        request = DescribeDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(domain)
        response = client.do_action_with_exception(request)
        data = {"code": 0, "data": response.decode(encoding='utf-8')}
        return data
    except Exception:
        return {"code": 1}


def Ali_Get_Parsing(key, secret, region, RecordId):
    try:
        client = AcsClient(key, secret, region)
        request = DescribeDomainRecordInfoRequest()
        request.set_accept_format('json')
        request.set_RecordId(RecordId)
        response = client.do_action_with_exception(request)
        data = {"code": 0, "data": response.decode(encoding='utf-8')}
        return data
    except Exception:
        return {"code": 1}


def Ali_Edit_Parsing(key, secret, region, domain=None, **kwargs):
    try:
        client = AcsClient(key, secret, region)
        if kwargs['RecordId']:
            request = UpdateDomainRecordRequest()
            request.set_accept_format('json')
            request.set_RecordId(kwargs['RecordId'])
        else:
            request = AddDomainRecordRequest()
            request.set_accept_format('json')
            request.set_DomainName(domain)
        request.set_RR(kwargs['RR'])
        request.set_Type(kwargs['Type'])
        request.set_Value(kwargs['Value'])
        request.set_TTL(kwargs['TTL'])
        request.set_Line(kwargs['Line'])
        if kwargs['Priority']:
            request.set_Priority(int(kwargs['Priority']))
        response = client.do_action_with_exception(request)
        data = {"code": 0, "data": response.decode(encoding='utf-8')}
        return data
    except Exception:
        return {"code": 1}


def Ali_Del_Parsing(key, secret, region, RecordId):
    try:
        client = AcsClient(key, secret, region)
        request = DeleteDomainRecordRequest()
        request.set_accept_format('json')
        request.set_RecordId(RecordId)
        response = client.do_action_with_exception(request)
        data = {"code": 0, "data": response.decode(encoding='utf-8')}
        return data
    except Exception:
        return {"code": 1}


def Ali_Add_Domain(key, secret, region, domain):
    try:
        client = AcsClient(key, secret, region)
        request = AddDomainRequest()
        request.set_accept_format('json')
        request.set_DomainName(domain)
        response = client.do_action_with_exception(request)
        data = {"code": 0, "data": response.decode(encoding='utf-8')}
        return data
    except Exception:
        return {"code": 1}
