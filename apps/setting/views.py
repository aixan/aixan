from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.setting.models import Setting, Menu
from apps.user.models import Role, User
from apps.setting.forms import MenuForm
from apps.lib.set import user_get
import json
import time
import datetime


def clear(request):
    data = {"code": 1, "msg": "服务端清理缓存成功"}
    return HttpResponse(json.dumps(data))


def setting(request):
    data = Setting.objects.all()
    di_ct = {}
    for i in data:
        if i.key == "public_key":
            di_ct['public_key'] = i.value
        elif i.key == "private_key":
            di_ct['private_key'] = i.value
    return render(request, "setting/setting.html", di_ct)


def get_key(request):
    if request.method == "GET":
        data = Setting.objects.all()
    elif request.method == "POST":
        user = user_get(request)
        public_key = request.POST.get("public_key")
        private_key = request.POST.get("private_key")

        obj_public_key = Setting.objects.update_or_create(key="public_key", defaults={"value": public_key},
                                                          created_by=user)
        print(obj_public_key)
        obj_private_key = Setting.objects.update_or_create(key="private_key", defaults={"value": private_key},
                                                           created_by=user)
        print(obj_private_key)
        data = {"code": 0, "msg": "修改成功."}
        return JsonResponse(data)


def menuIn(user):
    tree = []
    if user == True:
        data = Menu.objects.filter(status=1, pid_id=None).order_by('sort')
        for menu in data:
            menu_data = {
                "title": menu.title,
                "icon": menu.icon,
                "href": menu.href,
                "target": menu.target,
                "child": []
            }
            childs = Menu.objects.filter(status=1, pid_id=menu.id).order_by('sort')
            if childs:
                menu_data["child"] = get_child_menu(user, childs)
            tree.append(menu_data)
    else:
        data = Role.objects.filter(user__username=user,
                                   menu__status=1,
                                   menu__pid__id=None
                                   ).order_by('menu__sort').values(
            "menu__id",
            "menu__pid",
            "menu__title",
            "menu__icon",
            "menu__href",
            "menu__target",
        ).distinct()
        for menu in data:
            menu_data = {
                "title": menu["menu__title"],
                "icon": menu["menu__icon"],
                "href": menu["menu__href"],
                "target": menu["menu__target"],
                "child": []
            }
            childs = Role.objects.filter(user__username=user,
                                         menu__status=1,
                                         menu__pid_id=menu["menu__id"]
                                         ).order_by(
                'menu__sort').values(
                "menu__id",
                "menu__pid",
                "menu__title",
                "menu__icon",
                "menu__href",
                "menu__target",
            ).distinct()
            if childs:
                menu_data["child"] = get_child_menu(user, childs)
            tree.append(menu_data)
    return tree


# 递归获取所有的子菜单
def get_child_menu(user, childs):
    if childs:
        child = []
        if user == True:
            for children in childs:
                data = {
                    "title": children.title,
                    "href": children.href,
                    "icon": children.icon,
                    "target": children.target,
                    "child": []
                }
                _childs = Menu.objects.filter(status=1, pid__id=children.id).order_by('sort')
                if _childs:
                    data["child"] = get_child_menu(user, _childs)
                child.append(data)
        else:
            for children in childs:
                data = {
                    "title": children["menu__title"],
                    "href": children["menu__href"],
                    "icon": children["menu__icon"],
                    "target": children["menu__target"],
                    "child": []
                }
                _childs = Role.objects.filter(user__username=user,
                                              menu__status=1,
                                              menu__pid__id=children["menu__id"]
                                              ).order_by('menu__sort').values(
                    "menu__id",
                    "menu__pid",
                    "menu__title",
                    "menu__icon",
                    "menu__href",
                    "menu__target",
                ).distinct()
                if _childs:
                    data["child"] = get_child_menu(user, _childs)
                child.append(data)
        return child


def get_menu(request):
    user = user_get(request)
    if user.is_superuser:
        menuInfo = menuIn(user.is_superuser)
    else:
        menuInfo = menuIn(user.username)
    homeInfo = {
        "title": "首页",
        "href": "home.html"
    }
    logoInfo = {
        "title": "运维管理平台",
        "image": "/static/layuimini/images/logo.png",
        "href": ""
    }
    systemInit = {
        "homeInfo": homeInfo,
        "logoInfo": logoInfo,
        "menuInfo": menuInfo,
    }
    return JsonResponse(systemInit)


def menu(request):
    if request.method == "GET":
        return render(request, "setting/menu.html")
    if request.method == "POST":
        id = request.POST.get("id")
        Menu.objects.get(id=id).delete()
        data = {"code": 0, "msg": "删除成功"}
        return JsonResponse(data)


def menu_set(request):
    data = Menu.objects.all().order_by('sort')
    list = []
    for item in data:
        dict = {}
        dict["authorityId"] = item.id
        dict["authorityName"] = item.title
        dict["orderNumber"] = item.sort
        dict["menuUrl"] = item.href
        dict["menuIcon"] = item.icon
        dict["status"] = item.status
        dict["target"] = item.target
        if not item.pid_id:
            pid = -1
        else:
            pid = item.pid_id
        dict["parentId"] = pid
        dict["authority"] = ""
        dict["checked"] = 0
        list.append(dict)
    data = {"code": 0, "msg": "", "count": "", "data": list}
    return HttpResponse(json.dumps(data))


def add_menu_get1():
    data = Menu.objects.filter(pid_id=None).order_by('sort')
    tree = []
    for item in data:
        data = {
            "title": item.title,
            "id": item.id,
            "children": []
        }
        children = Menu.objects.filter(pid_id=item.id).order_by('sort')
        if children:
            data["children"] = add_menu_get2(children)
        tree.append(data)
    return tree


def add_menu_get2(children):
    childrens = []
    if children:
        for children in children:
            data = {
                "title": children.title,
                "id": children.id,
                "children": []
            }
            _childs = Menu.objects.filter(pid_id=children.id).order_by('sort')
            if _childs:
                data["children"] = add_menu_get2(_childs)
            childrens.append(data)
    return childrens


def add_menu(request):
    if request.method == "GET":
        return render(request, "setting/add_menu.html")
    elif request.method == "MENU":
        data = add_menu_get1()
        data = {"code": 0, "msg": "获取成功", "data": data}
        return JsonResponse(data)
    elif request.method == "POST":
        menuf = MenuForm(request.POST)
        if menuf.is_valid():
            menuf.save()
            data = {"code": 0, "msg": "菜单添加成功"}
        else:
            data = {"code": 1, "msg": "菜单添加失败"}
        return JsonResponse(data)


def edit_menu(request):
    if request.method == "GET":
        id = request.GET.get("id")
        data = Menu.objects.get(id=id)
        dict = {}
        dict["id"] = id
        if data.pid:
            dict["pid"] = data.pid.id
        else:
            dict["pid"] = ""
        dict["title"] = data.title
        dict["icon"] = data.icon
        dict["sort"] = data.sort
        dict["href"] = data.href
        dict["status"] = data.status
        dict["target"] = data.target
        return render(request, "setting/edit_menu.html", dict)
    elif request.method == "MENU":
        data = add_menu_get1()
        data = {"code": 0, "msg": "获取成功", "data": data}
        return JsonResponse(data)
    elif request.method == "POST":
        id = request.POST.get("id")
        menu_obj = Menu.objects.get(id=id)
        menuf = MenuForm(request.POST, instance=menu_obj)
        if menuf.is_valid():
            menuf.save()
            data = {"code": 0, "msg": "菜单修改成功"}
        else:
            data = {"code": 0, "msg": "菜单修改失败"}
        return JsonResponse(data)
