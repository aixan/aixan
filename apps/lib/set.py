from apps.user.models import User


def user_get(request):
    did = request.session["id"]
    user = User.objects.get(id=did)
    return user
