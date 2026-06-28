from members.models import MemberApplication


def pending_applications(request):
    user = getattr(request, "user", None)
    tenant = getattr(request, "tenant", None)
    if not user or not user.is_authenticated or tenant is None:
        return {"pending_applications_count": 0}
    if not (user.is_superuser or user.id == 1):
        return {"pending_applications_count": 0}
    count = MemberApplication.objects.filter(
        tenant=tenant,
        status=MemberApplication.STATUS_PENDING,
    ).count()
    return {"pending_applications_count": count}
