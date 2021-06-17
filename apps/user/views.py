from django.shortcuts import render
from django.contrib.auth import get_user_model
from apps.user.forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, QueryDict
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json
from apps.lib.utils import human_datetime
from apps.setting.models import Menu
from apps.user.models import Role
from apps.lib.set import user_get

User = get_user_model()


def loginView(request):
    if request.method == "GET":
        return render(request, 'user/login.html')
    elif request.method == 'POST':
        remember = request.POST.get("remember")
        user = authenticate(request, **request.POST)
        if user and user.is_active:  # 如果验证成功且用户已激活执行下面代码
            login(request, user)  # 使用自带的login函数进行登录，会自动添加session信息
            request.session["id"] = user.id  # 自定义session，login函数添加的session不满足时可以增加自定义的session信息。
            if remember:
                request.session.set_expiry(0)  # 0代表关闭浏览器session失效
            else:
                request.session.set_expiry(None)  # 设置session过期时间，None表示使用系统默认的过期时间
            return JsonResponse({"code": 0, "msg": "登录成功"})
        elif user and not user.is_active:
            return JsonResponse({"code": 1, "msg": "该用户还没有激活，请<a href='#'>激活</a>"})
        else:
            return JsonResponse({"code": 1, "msg": "账号或密码错误"})


def logoutView(request):
    logout(request)  # 调用django自带退出功能，会帮助我们删除相关session
    return redirect(request.META["HTTP_REFERER"])


# 编辑用户信息
@login_required
def edit(request, id):
    user = User.objects.get(id=id)
    # user_id 是 OneToOneField 自动生成的字段
    if User.objects.filter(id=id).exists():
        profile = User.objects.get(id=id)
    else:
        profile = User.objects.create(user=user)
    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if user.is_staff or request.user == user:
            profile_form = UserForm(request.POST, request.FILES)
            if profile_form.is_valid():
                # 取得清洗后的合法数据
                profile_cd = profile_form.cleaned_data
                profile.phone = profile_cd['phone']
                profile.desc = profile_cd['desc']
                profile.name = profile_cd['name']
                profile.sex = profile_cd['sex']
                profile.email = profile_cd['email']
                profile.card_id = profile_cd['card_id']
                profile.home_address = profile_cd['home_address']
                profile.save()
                # 带参数的 redirect()
                data = {"code": 0, "msg": "用户信息修改成功~"}
            else:
                data = {"code": 1, "msg": "注册表单输入有误。请重新输入~"}
            return JsonResponse(data)
        else:
            data = {"code": 1, "msg": "你没有权限修改此用户信息。"}
            return JsonResponse(data)
    elif request.method == 'GET':
        profile_form = UserForm()
        context = {'profile_form': profile_form, 'profile': profile, 'user': user}
        return render(request, 'user/edit.html', context)


@login_required
def password(request, id):
    if request.method == "POST":
        form = ChangepwdForm(request.POST.copy())
        if form.is_valid():
            username = User.objects.get(id=id)
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["new_password"]
            again_password = form.cleaned_data["again_password"]
            user = authenticate(username=username, password=old_password)
            if user:  # 原口令正确
                if new_password == again_password:  # 两次新口令一致
                    user.set_password(new_password)
                    user.save()
                    data = {"code": 0, "msg": "修改密码成功，请重新登录~"}
                    return JsonResponse(data)
                else:  # 两次新口令不一致
                    data = {"code": 1, "msg": "修改密码失败,两次新密码不一致~"}
                    return JsonResponse(data)
            else:  # 原口令不正确
                if new_password == again_password:  # 两次新口令一致
                    data = {"code": 1, "msg": "原密码错误，请重新输入~"}
                    return JsonResponse(data)
                else:  # 两次新口令不一致
                    data = {"code": 1, "msg": "修改密码失败,两次新密码不一致~"}
                    return JsonResponse(data)
    elif request.method == 'GET':
        return render(request, 'user/password.html')


def get_auth(request):
    return render(request, 'user/auth.html')


def account(request):
    return render(request, 'user/account.html')


def get_account(request):
    user = User.objects.filter(deleted_by_id__isnull=True)
    dataCount = user.count()
    pageIndex = request.GET.get("pageIndex")
    pageSize = request.GET.get("pageSize")

    li_st = []
    res = []
    for item in user:
        di_ct = {'id': item.id, 'username': item.username, 'name': item.name, 'sex': item.sex, 'phone': item.phone,
                 'email': item.email, 'desc': item.desc, 'is_active': item.is_active}
        date = item.last_login
        if not date:
            date = ""
        else:
            date = item.last_login.strftime("%Y-%m-%d %H:%M:%S")
        di_ct['last_login'] = date
        # role = []
        # for item in item.roles.all():
        #     role.append(item.name)
        # di_ct['role'] = role
        li_st.append(di_ct)
    pageInator = Paginator(li_st, pageSize)
    context = pageInator.page(pageIndex)
    for item in context:
        res.append(item)
    data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
    return HttpResponse(json.dumps(data))


def edit_user(request):
    if request.method == 'GET':
        did = request.GET.get('id', None)
        data = Role.objects.filter(deleted_at__isnull=True)
        li_st = []
        for item in data:
            di_ct = {"id": item.id, 'name': item.name}
            li_st.append(di_ct)
        if did:
            user = User.objects.get(id=did)
            context = {'id': did, 'profile': user, "role": li_st}
        else:
            context = {"role": li_st}
        return render(request, 'user/edit_user.html', context)

    elif request.method == 'POST':
        user = user_get(request)
        did = request.POST.get('id')
        data = {
            "username": request.POST.get("username"),
            "name": request.POST.get("name"),
            "sex": request.POST.get("sex"),
            "phone": request.POST.get("phone"),
            "email": request.POST.get("email"),
            "card_id": request.POST.get("card_id"),
            "home_address": request.POST.get("home_address"),
            "desc": request.POST.get("desc", None),
        }
        if did:
            if User.objects.filter(phone=data["phone"], deleted_by_id__isnull=True).exclude(id=did):
                return JsonResponse({"code": 1, "msg": "手机号已存在"})
            if User.objects.filter(email=data["email"], deleted_by_id__isnull=True).exclude(id=did):
                return JsonResponse({"code": 1, "msg": "邮箱已存在"})
            User.objects.filter(id=did).update(**data)
            data = {"code": 0, "msg": "用户资料修改成功~"}
        else:
            data["password"] = request.POST.get("password")
            if User.objects.filter(username=data["username"]).first():
                return JsonResponse({"code": 1, "msg": "用户名已存在"})
            if User.objects.filter(phone=data["phone"], deleted_by_id__isnull=True).first():
                return JsonResponse({"code": 1, "msg": "手机号已存在"})
            if User.objects.filter(email=data["email"], deleted_by_id__isnull=True).first():
                return JsonResponse({"code": 1, "msg": "邮箱已存在"})
            User.objects.create_user(created_by=user, **data)
            data = {"code": 0, "msg": "用户添加成功~"}
        return JsonResponse(data)
    elif request.method == "DELETE":
        user = user_get(request)
        request_data = QueryDict(request.body)
        did = request_data.get("id").split(",")
        User.objects.filter(id__in=did).update(deleted_at=human_datetime(), deleted_by=user, is_active=0)
        data = {"code": 0, "msg": "账号删除成功~"}
        return JsonResponse(data)


def active(request):
    get_id = request.POST.get('id')
    user = User.objects.get(id=get_id)
    if user.is_active:
        user.is_active = 0
        user.save()
        data = {"code": 0, "msg": "账户已禁用~"}
    else:
        user.is_active = 1
        user.save()
        data = {"code": 1, "msg": "账户已启用~"}
    return JsonResponse(data)


def passwd(request):
    get_id = request.POST.get('id')
    user = User.objects.get(id=get_id)
    new_password = request.POST.get('password')

    user.set_password(new_password)
    user.save()
    data = {"code": 0, "msg": "修改密码成功~"}
    return JsonResponse(data)


def search_user(request):
    username = request.GET.get("username", None)
    name = request.GET.get("name", None)
    phone = request.GET.get("phone", None)
    email = request.GET.get("email", None)

    data = User.objects.filter(username__contains=username, name__contains=name, phone__contains=phone,
                               email__contains=email, deleted_by__id__isnull=True)

    li_st = []
    for item in data:
        di_ct = {'id': item.id, 'username': item.username, 'name': item.name, 'sex': item.sex,
                 'phone': item.phone,
                 'email': item.email, 'desc': item.desc, 'is_active': item.is_active}
        date = item.last_login
        if not date:
            date = ""
        else:
            date = item.last_login.strftime("%Y-%m-%d %H:%M:%S")
        di_ct['last_login'] = date
        # role = []
        # for item in item.roles.all():
        #     role.append(item.name)
        # di_ct['role'] = role
        li_st.append(di_ct)

    data = {"code": 0, "msg": "ok", "DataCount": 1, "data": li_st}
    return HttpResponse(json.dumps(data))


def role(request):
    user = user_get(request)
    request_data = QueryDict(request.body)
    d_id = request_data.get('id', None)
    name = request_data.get('name', None)
    if request.method == "GET":
        return render(request, 'user/role.html')
    elif request.method == "POST":
        if Role.objects.filter(name=name, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "角色已存在，创建失败~"}
        else:
            Role.objects.create(name=name, created_by=user)
            data = {"code": 0, "msg": "角色创建成功~"}
        return JsonResponse(data)
    elif request.method == "PUT":
        if Role.objects.filter(name=name, deleted_by__id__isnull=True).exists():
            data = {"code": 1, "msg": "角色已存在，修改失败~"}
        else:
            Role.objects.filter(id=d_id).update(name=name)
            data = {"code": 0, "msg": "角色修改成功~"}
        return JsonResponse(data)
    elif request.method == "DELETE":
        Role.objects.filter(id__in=d_id.split(",")).update(deleted_at=human_datetime(), deleted_by=user)
        data = {"code": 0, "msg": "删除角色成功"}
        return JsonResponse(data)


def get_role(request):
    data = Role.objects.filter(deleted_by__id__isnull=True)
    dataCount = data.count()
    pageIndex = request.GET.get("pageIndex")
    pageSize = request.GET.get("pageSize")

    li_st = []
    res = []
    for item in data:
        di_ct = {'id': item.id, 'name': item.name, 'used': item.user.count()}
        li_st.append(di_ct)
    pageInator = Paginator(li_st, pageSize)
    context = pageInator.page(pageIndex)
    for item in context:
        res.append(item)
    data = {"code": 0, "msg": "ok", "DataCount": dataCount, "data": res}
    return HttpResponse(json.dumps(data))


def menu_auth(request):
    if request.method == "GET":
        did = request.GET.get("id")
        menu = Menu.objects.filter(role__id=did)
        value = []
        for i in menu:
            value.append(i.id)
        data = Menu.objects.all()
        li_st = []
        for item in data:
            di_ct = {'value': item.id, 'title': item.title}
            li_st.append(di_ct)
        data = {"code": 0, "data": li_st, "value": value}
        return JsonResponse(data)
    elif request.method == "POST":
        id = request.POST.get("id")
        types = request.POST.get("types")
        data = eval(request.POST.get('data'))
        list = []
        for item in data:
            list.append(item['value'])
        obj = Role.objects.get(id=id)
        menu = Menu.objects.filter(id__in=list)
        if types == "add":
            obj.menu_set.add(*menu)
        else:
            obj.menu_set.remove(*menu)
        obj.save()
        data = {"code": 0, "msg": "菜单权限变更成功"}
        return JsonResponse(data)


def role_user(request):
    if request.method == "GET":
        did = request.GET.get("id")
        role = Role.objects.get(id=did)
        value = []
        for i in role.user.all():
            value.append(i.id)
        data = User.objects.filter(deleted_by__id__isnull=True)
        li_st = []
        for item in data:
            di_ct = {'value': item.id, 'title': item.name}
            li_st.append(di_ct)
        data = {"code": 0, "data": li_st, "value": value}
        return JsonResponse(data)
    elif request.method == "POST":
        did = request.POST.get("did")
        types = request.POST.get("types")
        data = eval(request.POST.get('data'))
        list = []
        for item in data:
            list.append(item['value'])
        obj = Role.objects.get(id=id)
        user = User.objects.filter(id__in=list)
        if types == "add":
            obj.user.add(*user)
        else:
            obj.user.remove(*user)
        obj.save()
        data = {"code": 0, "msg": "角色用户变更成功"}
        return JsonResponse(data)
