from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.info.models import Alarm, Heartbeat
import time
from apps.lib.weixin import *
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def add_number(request):
    if request.method == 'POST':
        # 判断POST请求body是否为空
        api = request.body.decode("utf8")
        if (request.body.decode() == '') and (api[0:1]+api[-1] != "{}"):
            date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data = {'status': 1, 'msg': "NO", 'date': date}
            return JsonResponse(data)
        else:
            # body = eval(api)
            body = eval(json.loads(api))
        # 确保字段不为空
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if body['state'] == "AIXAN":
            # 添加当前时间到xintiao表
            get_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            obj = Heartbeat.objects.create(time=get_time)
            obj.save()
            data = {'status': 0, 'msg': "OK", 'date': date}
            return JsonResponse(data)
        elif body['state'] == '故障':
            state = body['state']
            IP = body['IP']
            why = body['why']
            f_time = body['f_time']
            problem = body['problem']
            c_state = body['c_state']
            e_id = body['e_id']

            # 写入数据库
            obj = Alarm.objects.create(
                state=state,
                IP=IP,
                why=why,
                f_time=f_time.replace('.', '-'),
                problem=problem,
                c_state=c_state,
                e_id=e_id
            )
            obj.save()
            data = f"#### {state}IP:{IP}\n" \
                   f"<font color='warning'>故障ID</font>:{e_id}\n" \
                   f"<font color='warning'>故障类型</font>:{problem}\n" \
                   f"<font color='warning'>故障原因</font>:{why}\n" \
                   f"<font color='warning'>故障时间</font>:{f_time.replace('.', '-')}"
            weiXin("HeShuaiYong", data)
            data = {'status': 0, 'msg': "OK", 'date': date}
            return JsonResponse(data)
        elif body['state'] == '已恢复':
            state = body['state']
            IP = body['IP']
            r_time = body['r_time']
            e_time = body['e_time']
            c_state = body['c_state']
            e_id = body['e_id']
            why = body['why']
            f_time = body['f_time']
            problem = body['problem']

            h = Alarm.objects.filter(e_id=e_id).count()
            if h == 1:
                print(h + body)
            elif h == 0:
                obj = Alarm.objects.create(
                    state=state,
                    IP=IP,
                    why=why,
                    e_time=e_time,
                    f_time=f_time.replace('.', '-'),
                    r_time=r_time.replace('.', '-'),
                    problem=problem,
                    c_state=c_state,
                    e_id=e_id
                )
                obj.save()
                data = f"#### {state}IP:{IP}\n" \
                       f"<font color='info'>恢复ID</font>:{e_id}\n" \
                       f"<font color='info'>持续时间</font>:{e_time}\n" \
                       f"<font color='info'>故障类型</font>:{problem}\n" \
                       f"<font color='info'>恢复原因</font>:{why}\n" \
                       f"<font color='info'>故障时间</font>:{f_time.replace('.', '-')}\n" \
                       f"<font color='info'>恢复时间</font>:{r_time.replace('.', '-')}"
                weiXin("HeShuaiYong", data)
            else:
                print(h + body)
            data = {'status': 0, 'msg': "OK", 'date': date}
            return JsonResponse(data)
        else:
            data = {'status': 1, 'msg': "NO", 'date': date}
            return JsonResponse(data)
