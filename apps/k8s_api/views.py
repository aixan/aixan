from django.shortcuts import render
import hashlib
import json
import os
import random
from datetime import datetime
import OpenSSL
import yaml
from django.core.paginator import Paginator
from django.http import JsonResponse, QueryDict, HttpResponse
from django.shortcuts import render
from kubernetes import client

from apps.host.models import Host
from apps.k8s.models import K8s, Auth
from apps.lib.k8s import dt_format, auth_config
from apps.user.models import User
from apps.lib.set import user_get


def yaml_edit(request):
    dict = {}
    hostname = request.GET.get('hostname')
    namespace = request.GET.get('namespace', None)
    resource = request.GET.get('resource', None)
    name = request.GET.get('name', None)
    types = request.GET.get('types')
    dict['hostname'] = hostname
    dict['namespace'] = namespace
    dict['resource'] = resource
    dict['name'] = name
    dict['types'] = types
    return render(request, 'k8s_api/yaml_edit.html', dict)


def json_edit(request):
    dict = {}
    hostname = request.GET.get('hostname')
    namespace = request.GET.get('namespace', None)
    resource = request.GET.get('resource', None)
    name = request.GET.get('name', None)
    dict['hostname'] = hostname
    dict['namespace'] = namespace
    dict['resource'] = resource
    dict['name'] = name
    return render(request, 'k8s_api/json_edit.html', dict)


def node(request):
    return render(request, 'k8s_api/node.html')


def namespace(request):
    return render(request, 'k8s_api/namespace.html')


def pv(request):
    return render(request, 'k8s_api/pv.html')


def add_pv(request):
    return render(request, 'k8s_api/add_pv.html')


def deployment(request):
    return render(request, 'k8s_api/deployment.html')


def service(request):
    return render(request, 'k8s_api/service.html')


def daemonset(request):
    return render(request, 'k8s_api/daemonset.html')


def statefulset(request):
    return render(request, 'k8s_api/statefulset.html')


def pod(request):
    return render(request, 'k8s_api/pod.html')


def add_pod(request):
    return render(request, 'k8s_api/add_pod.html')


def cronjobs(request):
    return render(request, 'k8s_api/cronjobs.html')


def jobs(request):
    return render(request, 'k8s_api/jobs.html')


def ingress(request):
    return render(request, 'k8s_api/ingress.html')


def pvc(request):
    return render(request, 'k8s_api/pvc.html')


def configmap(request):
    return render(request, 'k8s_api/configmap.html')


def secret(request):
    return render(request, 'k8s_api/secret.html')


def error(e):
    status = getattr(e, "status")
    if status == 403:
        data = {'code': 1, 'msg': "没有访问权限"}
    else:
        data = {'code': 1, 'msg': "获取数据失败"}
    return data


def get_node(request):
    # 命名空间选择和命名空间表格使用
    if request.method == "GET":
        user = user_get(request)
        hostname = request.GET.get('hostname')

        auth_config(user, hostname)
        core_api = client.CoreV1Api()

        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for node in core_api.list_node_with_http_info()[0].items:
                dict = {}
                dict["name"] = node.metadata.name
                dict["labels"] = node.metadata.labels
                status = node.status.conditions[-1].status
                if status:
                    dict["status"] = "Ready"
                else:
                    dict["status"] = status
                dict["scheduler"] = ("是" if node.spec.unschedulable is None else "否")
                dict["cpu"] = node.status.capacity['cpu']
                dict["memory"] = node.status.capacity['memory']
                dict["kebelet_version"] = node.status.node_info.kubelet_version
                dict["cri_version"] = node.status.node_info.container_runtime_version
                dict["create_time"] = dt_format(node.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_pv(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    core_api = client.CoreV1Api()

    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for pv in core_api.list_persistent_volume().items:
                dict = {}
                dict["name"] = pv.metadata.name
                dict["capacity"] = pv.spec.capacity["storage"]
                dict["access_modes"] = pv.spec.access_modes
                dict["reclaim_policy"] = pv.spec.persistent_volume_reclaim_policy
                dict["status"] = pv.status.phase
                if pv.spec.claim_ref is not None:
                    pvc_ns = pv.spec.claim_ref.namespace
                    pvc_name = pv.spec.claim_ref.name
                    dict["pvc"] = "%s / %s" % (pvc_ns, pvc_name)
                else:
                    dict["pvc"] = "未绑定"
                dict["tsorage_class"] = pv.spec.storage_class_name
                dict["create_time"] = dt_format(pv.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        try:
            core_api.delete_persistent_volume(name)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "POST":
        name = request.POST.get("name", None)
        capacity = request.POST.get("capacity", None)
        access_mode = request.POST.get("access_mode", None)
        storage_type = request.POST.get("storage_type", None)
        server_ip = request.POST.get("server_ip", None)
        mount_path = request.POST.get("mount_path", None)
        body = client.V1PersistentVolume(
            api_version="v1",
            kind="PersistentVolume",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1PersistentVolumeSpec(
                capacity={'storage': capacity},
                access_modes=[access_mode],
                nfs=client.V1NFSVolumeSource(
                    server=server_ip,
                    path="/ifs/kubernetes/%s" % mount_path
                )
            )
        )
        try:
            core_api.create_persistent_volume(body=body)
            data = {"code": 0, "msg": "创建成功"}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_namespace(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    core_api = client.CoreV1Api()

    if request.method == "GET":
        list = []
        res = []
        try:
            for ns in core_api.list_namespace().items:
                dict = {}
                dict["name"] = ns.metadata.name
                dict["labels"] = ns.metadata.labels
                dict["phase"] = ns.status.phase
                dict["create_time"] = dt_format(ns.metadata.creation_timestamp)
                list.append(dict)
            if request.GET.get("pageIndex"):
                pageIndex = request.GET.get("pageIndex")
                pageSize = request.GET.get("pageSize")
                pageInator = Paginator(list, pageSize)
                context = pageInator.page(pageIndex)
                for item in context:
                    res.append(item)
            else:
                res = list
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        try:
            core_api.delete_namespace(name)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "ADD":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        labels = request_data.get("labels")
        try:
            dict = {}
            if not labels:
                pass
            else:
                labels = request_data.get("labels").split(",")
                for label in labels:
                    i, b = label.split(":")
                    dict[f"{i}"] = b
            body = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": name,
                    "labels": dict
                }
            }
            core_api.create_namespace(body)
            data = {"code": 0, "msg": "添加成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "EDIT":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        labels = request_data.get("labels")
        try:
            body = core_api.read_namespace(name)
            dict = {}

            if not labels:
                body.metadata.labels = None
            else:
                labels = request_data.get("labels").split(",")
                for label in labels:
                    i, b = label.split(":")
                    dict[f"{i}"] = b
                body.metadata.labels = dict
            core_api.replace_namespace(name, body)  # 全局更新
            # core_api.patch_namespace(name=name, body=body)  # 局部更新
            data = {"code": 0, "msg": "修改成功.", "data": dict}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_deployment(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    apps_api = client.AppsV1Api()
    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for dp in apps_api.list_namespaced_deployment(namespace).items:
                dict = {}
                dict["name"] = dp.metadata.name
                dict["namespace"] = dp.metadata.namespace
                dict["replicas"] = dp.spec.replicas
                dict["available_replicas"] = (
                    0 if dp.status.available_replicas is None else dp.status.available_replicas)
                dict["labels"] = dp.metadata.labels
                dict["selector"] = dp.spec.selector.match_labels
                if len(dp.spec.template.spec.containers) > 1:
                    images = ""
                    n = 1
                    for c in dp.spec.template.spec.containers:
                        status = ("运行中" if dp.status.conditions[0].status == "True" else "异常")
                        image = c.image
                        images += "[%s]: %s / %s" % (n, image, status)
                        images += "<br>"
                        n += 1
                else:
                    status = (
                        "运行中" if dp.status.conditions[0].status == "True" else "异常")
                    image = dp.spec.template.spec.containers[0].image
                    images = "%s / %s" % (image, status)
                dict["images"] = images
                dict["create_time"] = dt_format(dp.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            apps_api.delete_namespaced_deployment(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "REPLICAS":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        replicas = request_data.get('replicas')
        try:
            body = apps_api.read_namespaced_deployment(name, namespace)
            body.spec.replicas = int(replicas)
            apps_api.replace_namespaced_deployment(name, namespace, body)
            data = {"code": 0, "msg": "修改成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_service(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    core_api = client.CoreV1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for service in core_api.list_namespaced_service(namespace).items:
                dict = {}
                dict["name"] = service.metadata.name
                dict["namespace"] = service.metadata.namespace
                dict["labels"] = service.metadata.labels
                dict["type"] = service.spec.type
                dict["cluster_ip"] = service.spec.cluster_ip
                dict["selector"] = service.spec.selector
                ports = []
                for p in service.spec.ports:  # 不是序列，不能直接返回
                    port_name = p.name
                    port = p.port
                    target_port = p.target_port
                    protocol = p.protocol
                    node_port = ""
                    if dict["type"] == "NodePort":
                        node_port = " <br> NodePort: %s" % p.node_port

                    port = {'port_name': port_name, 'port': port, 'protocol': protocol, 'target_port': target_port,
                            'node_port': node_port}
                    ports.append(port)
                dict["ports"] = ports
                # 确认是否关联Pod
                for ep in core_api.list_namespaced_endpoints(namespace).items:
                    if ep.metadata.name == dict["name"] and ep.subsets is None:
                        dict["endpoint"] = "未关联"
                    else:
                        dict["endpoint"] = "已关联"
                dict["create_time"] = dt_format(service.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        try:
            core_api.delete_namespaced_service(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_pod(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    core_api = client.CoreV1Api()

    if request.method == "GET":
        namespace = request.GET.get("namespace")
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for pods in core_api.list_namespaced_pod(namespace).items:
                dict = {}
                dict["name"] = pods.metadata.name
                dict["namespace"] = pods.metadata.namespace
                dict["pod_ip"] = pods.status.pod_ip
                dict["labels"] = pods.metadata.labels
                containers = []  # [{},{},{}]
                status = "None"
                # 只为None说明Pod没有创建（不能调度或者正在下载镜像）
                if pods.status.container_statuses is None:
                    status = pods.status.conditions[-1].reason
                    print(status)
                else:
                    for c in pods.status.container_statuses:
                        c_name = c.name
                        c_image = c.image
                        # 获取重启次数
                        restart_count = c.restart_count
                        # 获取容器状态
                        c_status = "None"
                        if c.ready is True:
                            c_status = "Running"
                        elif c.ready is False:
                            if c.state.waiting is not None:
                                c_status = c.state.waiting.reason
                            elif c.state.terminated is not None:
                                c_status = c.state.terminated.reason
                            elif c.state.last_state.terminated is not None:
                                c_status = c.last_state.terminated.reason

                        c = {'c_name': c_name, 'c_image': c_image, 'restart_count': restart_count, 'c_status': c_status}
                        containers.append(c)
                dict["containers"] = containers
                dict["phase"] = pods.status.phase
                dict["create_time"] = dt_format(pods.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            core_api.delete_namespaced_pod(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "LOG":
        request_data = QueryDict(request.body)
        name = request_data.get("name", None)
        namespace = request_data.get("namespace", None)
        # 目前没有对Pod多容器处理
        try:
            log_text = core_api.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=500)
            if len(log_text) == 0:
                data = {"code": 0, "msg": "获取日志成功", "data": "没有日志！"}
            else:
                data = {"code": 0, "msg": "获取日志成功", "data": log_text}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_daemonset(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    apps_api = client.AppsV1Api()

    if request.method == "GET":
        namespace = request.GET.get("namespace")
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for ds in apps_api.list_namespaced_daemon_set(namespace).items:
                dict = {}
                dict["name"] = ds.metadata.name
                dict["namespace"] = ds.metadata.namespace
                dict["desired_number"] = ds.status.desired_number_scheduled
                dict["available_number"] = ds.status.number_available
                dict["selector"] = ds.spec.selector.match_labels
                containers = {}
                for c in ds.spec.template.spec.containers:
                    containers[c.name] = c.image
                dict["containers"] = containers
                dict["labels"] = ds.metadata.labels
                dict["create_time"] = dt_format(ds.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            apps_api.delete_namespaced_daemon_set(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_cronjobs(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    batch_api = client.BatchV2alpha1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for cj in batch_api.list_namespaced_cron_job(namespace).items:
                dict = {}
                dict["name"] = cj.metadata.name
                dict["namespace"] = cj.metadata.namespace
                dict["schedule"] = cj.spec.schedule
                if cj.status.last_schedule_time:
                    dict["lastScheduleTime"] = dt_format(cj.status.last_schedule_time)
                else:
                    dict["lastScheduleTime"] = ""
                print(cj.status.last_schedule_time)
                dict["create_time"] = dt_format(cj.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            batch_api.delete_namespaced_cron_job(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_jobs(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    batch_api = client.BatchV1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for job in batch_api.list_namespaced_job(namespace).items:
                dict = {}
                dict["name"] = job.metadata.name
                dict["namespace"] = job.metadata.namespace
                # dict["desired_number"] = ds.status.desired_number_scheduled
                # dict["available_number"] = ds.status.number_available
                # dict["selector"] = ds.spec.selector.match_labels
                # containers = {}
                # for c in ds.spec.template.spec.containers:
                #     containers[c.name] = c.image
                # dict["containers"] = containers
                dict["labels"] = job.metadata.labels
                dict["create_time"] = dt_format(job.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        try:
            batch_api.delete_namespaced_cron_job(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_statefulset(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    apps_api = client.AppsV1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for sts in apps_api.list_namespaced_stateful_set(namespace).items:
                dict = {}
                dict["name"] = sts.metadata.name
                dict["namespace"] = sts.metadata.namespace
                dict["replicas"] = sts.spec.replicas
                dict["selector"] = sts.spec.selector.match_labels
                dict["service_name"] = sts.spec.service_name
                dict["ready_replicas"] = ("0" if sts.status.ready_replicas is None else sts.status.ready_replicas)
                # current_replicas = sts.status.current_replicas
                containers = {}
                for c in sts.spec.template.spec.containers:
                    containers[c.name] = c.image
                dict["containers"] = containers
                dict["labels"] = sts.metadata.labels
                dict["create_time"] = dt_format(sts.metadata.creation_timestamp)
                list.append(dict)
            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get('namespace')
        try:
            apps_api.delete_namespaced_stateful_set(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_ingress(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    networking_api = client.NetworkingV1beta1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for ing in networking_api.list_namespaced_ingress(namespace).items:
                dict = {}
                dict["name"] = ing.metadata.name
                dict["namespace"] = ing.metadata.namespace
                dict["service"] = "None"
                # dict["http_hosts"] = "None"
                for h in ing.spec.rules:
                    host = h.host
                    path = ("/" if h.http.paths[0].path is None else h.http.paths[0].path)
                    service_name = h.http.paths[0].backend.service_name
                    service_port = h.http.paths[0].backend.service_port
                    http_hosts = {'host': host, 'path': path, 'service_name': service_name,
                                  'service_port': service_port}
                dict["http_hosts"] = http_hosts
                # dict["https_hosts"] = "None"
                if ing.spec.tls is None:
                    https_hosts = ing.spec.tls
                else:
                    for tls in ing.spec.tls:
                        host = tls.hosts[0]
                        secret_name = tls.secret_name
                        https_hosts = {'host': host, 'secret_name': secret_name}
                dict["https_hosts"] = https_hosts
                dict["labels"] = ing.metadata.labels
                dict["create_time"] = dt_format(ing.metadata.creation_timestamp)
                list.append(dict)
            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            networking_api.delete_namespaced_ingress(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_pvc(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    core_api = client.CoreV1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for pvc in core_api.list_namespaced_persistent_volume_claim(namespace).items:
                dict = {}
                dict["name"] = pvc.metadata.name
                dict["namespace"] = pvc.metadata.namespace
                dict["labels"] = pvc.metadata.labels
                dict["storage_class_name"] = pvc.spec.storage_class_name
                dict["access_modes"] = pvc.spec.access_modes
                dict["capacity"] = (
                    pvc.status.capacity if pvc.status.capacity is None else pvc.status.capacity["storage"])
                dict["volume_name"] = pvc.spec.volume_name
                dict["status"] = pvc.status.phase
                dict["create_time"] = dt_format(pvc.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            core_api.delete_namespaced_persistent_volume_claim(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_configmap(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    core_api = client.CoreV1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for cm in core_api.list_namespaced_config_map(namespace).items:
                dict = {}
                dict["name"] = cm.metadata.name
                dict["namespace"] = cm.metadata.namespace
                dict["data_length"] = ("0" if cm.data is None else len(cm.data))
                dict["create_time"] = dt_format(cm.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            core_api.delete_namespaced_config_map(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def get_secret(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')

    auth_config(user, hostname)
    core_api = client.CoreV1Api()

    namespace = request.GET.get("namespace")
    if request.method == "GET":
        pageIndex = request.GET.get("pageIndex")
        pageSize = request.GET.get("pageSize")

        list = []
        res = []
        try:
            for secret in core_api.list_namespaced_secret(namespace).items:
                dict = {}
                dict["name"] = secret.metadata.name
                dict["namespace"] = secret.metadata.namespace
                dict["data_length"] = ("空" if secret.data is None else len(secret.data))
                dict["create_time"] = dt_format(secret.metadata.creation_timestamp)
                list.append(dict)

            pageInator = Paginator(list, pageSize)
            context = pageInator.page(pageIndex)
            for item in context:
                res.append(item)
            data = {"code": 0, "msg": "ok", "DataCount": len(list), "data": res}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)
    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")
        try:
            core_api.delete_namespaced_secret(name, namespace)
            data = {"code": 0, "msg": "删除成功."}
        except Exception as e:
            data = error(e)
        return JsonResponse(data)


def yaml_json(request):
    user = user_get(request)
    hostname = request.GET.get('hostname')
    auth_config(user, hostname)
    core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc
    apps_api = client.AppsV1Api()  # deployment
    batch1_api = client.BatchV1Api()
    batch2_api = client.BatchV2alpha1Api()
    networking_api = client.NetworkingV1beta1Api()  # ingress
    storage_api = client.StorageV1Api()  # storage_class

    if request.method == "GET":
        namespace = request.GET.get('namespace', None)
        resource = request.GET.get('resource', None)
        name = request.GET.get('name', None)
        types = request.GET.get('types')
        try:
            if resource == "namespace":
                result = core_api.read_namespace(name=name, _preload_content=False).read()
            elif resource == "deployment":
                result = apps_api.read_namespaced_deployment(name=name, namespace=namespace,
                                                             _preload_content=False).read()
            elif resource == "replicaset":
                result = apps_api.read_namespaced_replica_set(name=name, namespace=namespace,
                                                              _preload_content=False).read()
            elif resource == "daemonset":
                result = apps_api.read_namespaced_daemon_set(name=name, namespace=namespace,
                                                             _preload_content=False).read()
            elif resource == "statefulset":
                result = apps_api.read_namespaced_stateful_set(name=name, namespace=namespace,
                                                               _preload_content=False).read()
            elif resource == "pod":
                result = core_api.read_namespaced_pod(name=name, namespace=namespace, _preload_content=False).read()
            elif resource == "service":
                result = core_api.read_namespaced_service(name=name, namespace=namespace, _preload_content=False).read()
            elif resource == "ingress":
                result = networking_api.read_namespaced_ingress(name=name, namespace=namespace,
                                                                _preload_content=False).read()
            elif resource == "cronjob":
                result = batch2_api.read_namespaced_cron_job(name=name, namespace=namespace,
                                                             _preload_content=False).read()
            elif resource == "job":
                result = batch1_api.read_namespaced_job(name=name, namespace=namespace, _preload_content=False).read()
            elif resource == "pvc":
                result = core_api.read_namespaced_persistent_volume_claim(name=name, namespace=namespace,
                                                                          _preload_content=False).read()
            elif resource == "pv":
                result = core_api.read_persistent_volume(name=name, _preload_content=False).read()
            elif resource == "node":
                result = core_api.read_node(name=name, _preload_content=False).read()
            elif resource == "configmap":
                result = core_api.read_namespaced_config_map(name=name, namespace=namespace,
                                                             _preload_content=False).read()
            elif resource == "secret":
                result = core_api.read_namespaced_secret(name=name, namespace=namespace, _preload_content=False).read()
            result = str(result, "utf-8")  # bytes转字符串
            if types == "yaml":
                result = yaml.safe_dump(json.loads(result))  # str/dict -> json -> yaml
            else:
                result = json.dumps(json.loads(result), sort_keys=True, indent=2)
            data = {"code": 0, "msg": "", "data": result}
            return data
        except Exception as e:
            data = error(e)
            return data

    elif request.method == "POST":
        namespace = request.POST.get('namespace', None)
        resource = request.POST.get('resource', None)
        name = request.POST.get('name', None)
        types = request.POST.get('types')
        if types == "yaml":
            body = request.POST.get('yaml', None)
            body = yaml.load(body)
        else:
            body = request.POST.get('json', None)
        try:
            if resource == "namespace":
                if name == body['metadata']['name']:
                    # core_api.replace_namespace(name, yaml.load(body))  # 全局更新
                    core_api.patch_namespace(name, body)  # 局部更新
                    data = {"code": 0, "msg": "更新成功"}
                else:
                    data = {"code": 1, "msg": "名字不对"}
            elif resource == "deployment":
                if name == body['metadata']['name']:
                    apps_api.patch_namespaced_deployment(name, namespace, body)  # 局部更新
                    data = {"code": 0, "msg": "更新成功"}
                else:
                    data = {"code": 1, "msg": "名字不对"}
            elif resource == "pod":
                if name == body['metadata']['name']:
                    core_api.patch_namespaced_pod(name, namespace, body)  # 局部更新
                    data = {"code": 0, "msg": "更新成功"}
                else:
                    data = {"code": 1, "msg": "名字不对"}
            elif resource == "service":
                if name == body['metadata']['name']:
                    core_api.patch_namespaced_service(name, namespace, body)  # 局部更新
                    data = {"code": 0, "msg": "更新成功"}
                else:
                    data = {"code": 1, "msg": "名字不对"}
            elif resource == "statefulset":
                if name == body['metadata']['name']:
                    apps_api.patch_namespaced_stateful_set(name, namespace, body)  # 局部更新
                    data = {"code": 0, "msg": "更新成功"}
                else:
                    data = {"code": 1, "msg": "名字不对"}
            return data
        except Exception as e:
            data = error(e)
            return data


def get_yaml(request):
    data = yaml_json(request)
    return JsonResponse(data)


def get_json(request):
    data = yaml_json(request)
    return JsonResponse(data)


def yaml_json_add(request):
    user = user_get(request)
    hostname = request.POST.get('hostname')
    auth_config(user, hostname)
    core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc
    apps_api = client.AppsV1Api()  # deployment
    batch1_api = client.BatchV1Api()
    batch2_api = client.BatchV2alpha1Api()
    networking_api = client.NetworkingV1beta1Api()  # ingress
    storage_api = client.StorageV1Api()  # storage_class
    namespace = request.POST.get('namespace', None)
    resource = request.POST.get('resource', None)
    name = request.POST.get('name', None)
    types = request.POST.get('types')
    if types == "yaml":
        body = request.POST.get('yaml', None)
        body = yaml.safe_load(body)
    else:
        body = request.POST.get('json', None)
    try:
        if body['kind'] == "Namespace":
            core_api.create_namespace(body)
        elif body['kind'] == "Deployment":
            apps_api.create_namespaced_deployment(namespace, body)
        elif body['kind'] == "DaemonSet":
            apps_api.create_namespaced_daemon_set(namespace, body)
        elif body['kind'] == "StatefulSet":
            apps_api.create_namespaced_stateful_set(namespace, body)
        elif body['kind'] == "Service":
            core_api.create_namespaced_service(namespace, body)
        elif body['kind'] == "Pod":
            core_api.create_namespaced_pod(namespace, body)
        elif body['kind'] == "Ingress":
            networking_api.create_namespaced_ingress(namespace, body)
        elif body['kind'] == "PersistentVolume":
            core_api.create_persistent_volume(body)
        elif body['kind'] == "PersistentVolumeClaim":
            core_api.create_namespaced_persistent_volume_claim(namespace, body)
        elif body['kind'] == "ConfigMap":
            core_api.create_namespaced_config_map(namespace, body)
        elif body['kind'] == "Secret":
            core_api.create_namespaced_secret(namespace, body)
        elif body['kind'] == "CronJob":
            batch2_api.create_namespaced_cron_job(namespace, body)
        elif body['kind'] == "Job":
            batch1_api.create_namespaced_job(namespace, body)
        data = {"code": 0, "msg": f"{body['kind']}创建成功"}
        return data
    except Exception as e:
        data = error(e)
        return data


def yaml_add(request):
    if request.method == "GET":
        dict = {}
        hostname = request.GET.get('hostname')
        namespace = request.GET.get('namespace', None)
        resource = request.GET.get('resource', None)
        name = request.GET.get('name', None)
        types = request.GET.get('types')
        dict['hostname'] = hostname
        dict['namespace'] = namespace
        dict['resource'] = resource
        dict['name'] = name
        dict['types'] = types
        return render(request, 'k8s_api/yaml_add.html', dict)
    elif request.method == "POST":
        data = yaml_json_add(request)
        return JsonResponse(data)


def json_add(request):
    if request.method == "GET":
        dict = {}
        hostname = request.GET.get('hostname')
        namespace = request.GET.get('namespace', None)
        resource = request.GET.get('resource', None)
        name = request.GET.get('name', None)
        types = request.GET.get('types')
        dict['hostname'] = hostname
        dict['namespace'] = namespace
        dict['resource'] = resource
        dict['name'] = name
        dict['types'] = types
        return render(request, 'k8s_api/json_add.html', dict)
    elif request.method == "POST":
        data = yaml_json_add(request)
        return JsonResponse(data)
