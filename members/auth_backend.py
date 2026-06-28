from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password

from .models import Member


class MemberBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        tenant = getattr(request, "tenant", None)
        qs = Member.objects.all()
        if tenant is not None:
            qs = qs.filter(tenant=tenant)

        normalized = "".join(str(username).split()).upper()
        try:
            member = qs.get(username=normalized)
        except Member.DoesNotExist:
            try:
                member = qs.get(membership_no=normalized)
            except Member.DoesNotExist:
                return None

        if not check_password(password, member.password or ""):
            return None

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=member.username,
            defaults={"email": member.email or ""},
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        return user
