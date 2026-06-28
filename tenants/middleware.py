from __future__ import annotations

from django.utils.deprecation import MiddlewareMixin

from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Resolve tenant using header or query string.
        request.tenant = None
        if request.path.startswith("/admin/"):
            return

        tenant_slug = request.headers.get("X-Tenant") or request.GET.get("tenant")
        if tenant_slug:
            request.tenant = Tenant.objects.filter(
                slug=tenant_slug,
                is_active=True,
            ).first()
            return

        # If a single tenant exists, assume it for local/dev usage.
        request.tenant = Tenant.objects.filter(is_active=True).first()
