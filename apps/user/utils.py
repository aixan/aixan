from django.contrib.auth.backends import BaseBackend, ModelBackend
from apps.user.models import User
from django.db.models import Q


class AuthBackend(BaseBackend):

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, **kwargs):
        data = kwargs
        try:
            user = User.objects.get(
                Q(username=data["username"][0]) | Q(email=data["username"][0]) | Q(phone=data["username"][0]),
                deleted_by_id__isnull=True
            )
        except User.DoesNotExist:
            return None
        return user if user.check_password(data["password"][0]) else None

    def has_perm(self, user_obj, perm, obj=None):
        print(user_obj.username)
