from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AnnouncementForm, DailyLiturgyForm, UpcomingEventForm
from .models import Announcement, DailyLiturgy, UpcomingEvent


class TenantMixin(LoginRequiredMixin):
    def get_tenant(self):
        return getattr(self.request, "tenant", None)

    def is_admin(self):
        user = self.request.user
        return user.is_superuser or user.id == 1

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = self.get_tenant()
        if tenant is None:
            return qs.none()
        return qs.filter(tenant=tenant)

    def form_valid(self, form):
        if hasattr(form, "instance") and form.instance is not None:
            form.instance.tenant = self.get_tenant()
        return super().form_valid(form)


class AnnouncementListView(TenantMixin, ListView):
    model = Announcement
    template_name = "content_app/announcements.html"
    context_object_name = "announcements"

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.GET.get("category", "")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["selected_category"] = self.request.GET.get("category", "")
        ctx["categories"] = Announcement.CATEGORY_CHOICES
        return ctx


class AnnouncementCreateView(TenantMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "content_app/announcement_form.html"
    success_url = reverse_lazy("content:announcements")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "New Announcement"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Announcement published.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AnnouncementUpdateView(TenantMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "content_app/announcement_form.html"
    success_url = reverse_lazy("content:announcements")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Announcement"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Announcement updated.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AnnouncementDeleteView(TenantMixin, DeleteView):
    model = Announcement
    template_name = "content_app/confirm_delete.html"
    success_url = reverse_lazy("content:announcements")

    def form_valid(self, form):
        messages.success(self.request, "Announcement deleted.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DailyLiturgyListView(TenantMixin, ListView):
    model = DailyLiturgy
    template_name = "content_app/liturgy_list.html"
    context_object_name = "liturgies"
    paginate_by = 10


class DailyLiturgyCreateView(TenantMixin, CreateView):
    model = DailyLiturgy
    form_class = DailyLiturgyForm
    template_name = "content_app/liturgy_form.html"
    success_url = reverse_lazy("content:liturgy")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Add Liturgy"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Liturgy saved.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DailyLiturgyUpdateView(TenantMixin, UpdateView):
    model = DailyLiturgy
    form_class = DailyLiturgyForm
    template_name = "content_app/liturgy_form.html"
    success_url = reverse_lazy("content:liturgy")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Liturgy"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Liturgy updated.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UpcomingEventListView(TenantMixin, ListView):
    model = UpcomingEvent
    template_name = "content_app/upcoming_events.html"
    context_object_name = "events"

    def get_queryset(self):
        return super().get_queryset().order_by("event_date", "-created_at")


class UpcomingEventCreateView(TenantMixin, CreateView):
    model = UpcomingEvent
    form_class = UpcomingEventForm
    template_name = "content_app/upcoming_event_form.html"
    success_url = reverse_lazy("content:upcoming-events")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "New Upcoming Event"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Upcoming event created.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UpcomingEventUpdateView(TenantMixin, UpdateView):
    model = UpcomingEvent
    form_class = UpcomingEventForm
    template_name = "content_app/upcoming_event_form.html"
    success_url = reverse_lazy("content:upcoming-events")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Upcoming Event"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Upcoming event updated.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class UpcomingEventDeleteView(TenantMixin, DeleteView):
    model = UpcomingEvent
    template_name = "content_app/upcoming_event_confirm_delete.html"
    success_url = reverse_lazy("content:upcoming-events")

    def form_valid(self, form):
        messages.success(self.request, "Upcoming event deleted.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
