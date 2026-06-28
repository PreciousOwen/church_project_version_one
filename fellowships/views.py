from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from members.models import Member

from .forms import FellowshipGroupForm, FellowshipParticipationForm
from .models import FellowshipGroup, FellowshipParticipation


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


class FellowshipGroupListView(TenantMixin, ListView):
    model = FellowshipGroup
    template_name = "fellowships/list.html"
    context_object_name = "groups"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.is_admin():
            return qs
        member = self.get_member()
        if not member:
            return qs.none()
        return qs.filter(fellowshipparticipation__member=member).distinct()


class FellowshipGroupDetailView(TenantMixin, DetailView):
    model = FellowshipGroup
    template_name = "fellowships/detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["participations"] = self.object.fellowshipparticipation_set.select_related(
            "member"
        )
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        if self.is_admin():
            return qs
        member = self.get_member()
        if not member:
            return qs.none()
        return qs.filter(fellowshipparticipation__member=member).distinct()


class FellowshipGroupCreateView(TenantMixin, CreateView):
    model = FellowshipGroup
    form_class = FellowshipGroupForm
    template_name = "fellowships/form.html"
    success_url = reverse_lazy("fellowships:list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Create Fellowship Group"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Fellowship group created.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class FellowshipGroupUpdateView(TenantMixin, UpdateView):
    model = FellowshipGroup
    form_class = FellowshipGroupForm
    template_name = "fellowships/form.html"

    def get_success_url(self):
        return reverse_lazy("fellowships:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Edit {self.object.name}"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Fellowship group updated.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class FellowshipGroupDeleteView(TenantMixin, DeleteView):
    model = FellowshipGroup
    template_name = "fellowships/confirm_delete.html"
    success_url = reverse_lazy("fellowships:list")

    def form_valid(self, form):
        messages.success(self.request, "Fellowship group deleted.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ParticipationCreateView(LoginRequiredMixin, CreateView):
    model = FellowshipParticipation
    form_class = FellowshipParticipationForm
    template_name = "fellowships/participation_form.html"
    success_url = reverse_lazy("fellowships:list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            form.fields["member"].queryset = Member.objects.filter(tenant=tenant)
            form.fields["group"].queryset = FellowshipGroup.objects.filter(
                tenant=tenant
            )
        return form

    def form_valid(self, form):
        form.instance.tenant = getattr(self.request, "tenant", None)
        messages.success(self.request, "Member added to fellowship.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.id == 1):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
