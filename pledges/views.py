import logging
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import CharField, Q, Sum
from django.db.models.functions import Cast
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from members.models import Member

from .forms import PledgeForm
from .models import Pledge

logger = logging.getLogger(__name__)


class TenantMixin(LoginRequiredMixin):
    def get_tenant(self):
        return getattr(self.request, "tenant", None)
    def is_admin(self):
        user = self.request.user
        return user.is_superuser or user.id == 1

    def get_member(self):
        tenant = self.get_tenant()
        if tenant is None:
            return None
        return Member.objects.filter(tenant=tenant, username=self.request.user.username).first()

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = self.get_tenant()
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def form_valid(self, form):
        form.instance.tenant = self.get_tenant()
        return super().form_valid(form)


class PledgeListView(TenantMixin, ListView):
    model = Pledge
    template_name = "pledges/list.html"
    context_object_name = "pledges"
    paginate_by = 20

    def _base_queryset(self):
        qs = super().get_queryset().select_related("member")
        if not self.is_admin():
            member = self.get_member()
            if not member:
                return qs.none()
            qs = qs.filter(member=member)
        return qs

    def _apply_period_filters(self, qs):
        year = (self.request.GET.get("year", "") or "").strip()
        if year:
            qs = qs.filter(year=year)

        season = (self.request.GET.get("season", "annual") or "annual").strip().lower()
        if season == "h1":
            qs = qs.filter(submission_date__month__gte=1, submission_date__month__lte=6)
        elif season == "h2":
            qs = qs.filter(submission_date__month__gte=7, submission_date__month__lte=12)
        return qs

    def _apply_search_filter(self, qs):
        search = (self.request.GET.get("q", "") or "").strip()
        if not search:
            return qs

        normalized = search.replace(",", "")
        amount = None
        try:
            amount = Decimal(normalized)
        except (InvalidOperation, ValueError):
            amount = None

        search_filter = (
            Q(member__full_name__icontains=search)
            | Q(year_text__icontains=normalized)
            | Q(building_text__icontains=normalized)
            | Q(stewardship_text__icontains=normalized)
            | Q(other_text__icontains=normalized)
        )
        if amount is not None:
            search_filter = search_filter | Q(building_pledge=amount) | Q(
                stewardship_pledge=amount
            ) | Q(other_pledges=amount)

        return qs.annotate(
            year_text=Cast("year", CharField()),
            building_text=Cast("building_pledge", CharField()),
            stewardship_text=Cast("stewardship_pledge", CharField()),
            other_text=Cast("other_pledges", CharField()),
        ).filter(search_filter)

    def get_queryset(self):
        qs = self._base_queryset()
        qs = self._apply_period_filters(qs)
        qs = self._apply_search_filter(qs)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["selected_year"] = self.request.GET.get("year", "")
        ctx["selected_season"] = self.request.GET.get("season", "annual")
        ctx["selected_query"] = self.request.GET.get("q", "")
        period_qs = self._apply_period_filters(self._base_queryset())
        totals = period_qs.aggregate(
            building_total=Sum("building_pledge"),
            stewardship_total=Sum("stewardship_pledge"),
            other_total=Sum("other_pledges"),
        )
        building_total = totals["building_total"] or Decimal("0")
        stewardship_total = totals["stewardship_total"] or Decimal("0")
        other_total = totals["other_total"] or Decimal("0")
        ctx["period_record_count"] = period_qs.count()
        ctx["building_total_display"] = f"{building_total:,.2f}"
        ctx["stewardship_total_display"] = f"{stewardship_total:,.2f}"
        ctx["other_total_display"] = f"{other_total:,.2f}"
        for pledge in ctx.get("pledges", []):
            pledge.building_pledge_display = f"{pledge.building_pledge:,.2f}"
            pledge.stewardship_pledge_display = f"{pledge.stewardship_pledge:,.2f}"
            pledge.other_pledges_display = f"{pledge.other_pledges:,.2f}"
        return ctx


class PledgeCreateView(TenantMixin, CreateView):
    model = Pledge
    form_class = PledgeForm
    template_name = "pledges/form.html"
    success_url = reverse_lazy("pledges:list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        tenant = self.get_tenant()
        if tenant:
            form.fields["member"].queryset = Member.objects.filter(tenant=tenant)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Record Pledge"
        return ctx

    def form_valid(self, form):
        logger.info("Pledge save attempt (valid): %s", form.cleaned_data)
        print("Pledge save attempt (valid):", form.cleaned_data)
        messages.success(self.request, "Pledge recorded successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning("Pledge save failed (invalid): %s", form.errors)
        print("Pledge save failed (invalid):", form.errors)
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PledgeUpdateView(TenantMixin, UpdateView):
    model = Pledge
    form_class = PledgeForm
    template_name = "pledges/form.html"
    success_url = reverse_lazy("pledges:list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        tenant = self.get_tenant()
        if tenant:
            form.fields["member"].queryset = Member.objects.filter(tenant=tenant)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Pledge"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Pledge updated.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PledgeDeleteView(TenantMixin, DeleteView):
    model = Pledge
    template_name = "pledges/confirm_delete.html"
    success_url = reverse_lazy("pledges:list")

    def form_valid(self, form):
        messages.success(self.request, "Pledge deleted.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
