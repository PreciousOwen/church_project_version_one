import logging

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView

from content_app.models import Announcement, UpcomingEvent
from fellowships.models import FellowshipGroup, FellowshipParticipation
from members.models import Member, MemberApplication
from pledges.models import Pledge

from .forms import (
    OtpVerifyForm,
    PasswordResetRequestForm,
    PasswordResetSetForm,
    PhoneLoginForm,
    PhoneSignupForm,
    TenantForm,
)
from .models import Tenant

logger = logging.getLogger(__name__)


class LandingView(TemplateView):
    """Public-facing landing page — no login required."""
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            ctx["upcoming_events"] = UpcomingEvent.objects.filter(
                tenant=tenant, is_active=True
            ).order_by("event_date", "-created_at")
        else:
            ctx["upcoming_events"] = []
        return ctx


class AboutView(TemplateView):
    template_name = "public/about.html"


class EventsView(TemplateView):
    template_name = "public/events.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            ctx["upcoming_events"] = UpcomingEvent.objects.filter(
                tenant=tenant, is_active=True
            ).order_by("event_date", "-created_at")[:6]
        else:
            ctx["upcoming_events"] = []
        return ctx


class MinistriesView(TemplateView):
    template_name = "public/ministries.html"


class ContactView(TemplateView):
    template_name = "public/contact.html"


PENDING_SIGNUP_USER_ID_SESSION_KEY = "pending_signup_user_id"
PENDING_SIGNUP_PHONE_SESSION_KEY = "pending_signup_phone"
PENDING_PASSWORD_RESET_USER_ID_SESSION_KEY = "pending_password_reset_user_id"
PENDING_PASSWORD_RESET_PHONE_SESSION_KEY = "pending_password_reset_phone"
PENDING_PASSWORD_RESET_VERIFIED_SESSION_KEY = "pending_password_reset_verified"


class SignupView(FormView):
    template_name = "signup.html"
    form_class = PhoneSignupForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        from django.contrib import messages
        from django.contrib.auth import get_user_model
        from django.utils.translation import gettext as _

        from .briq_otp import request_signup_otp

        User = get_user_model()

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        ok, err = request_signup_otp(phone_number=user.username)
        if not ok:
            logger.error("Signup OTP request failed for %s: %s", user.username, err)
            try:
                user.delete()
            except Exception:
                logger.exception("Failed to delete user %s after OTP failure.", user.id)
                from django.db import connection
                with connection.cursor() as c:
                    c.execute("DELETE FROM auth_user WHERE id = %s", [user.id])
            form.add_error(None, err or _("Failed to request verification code."))
            return self.form_invalid(form)

        self.request.session[PENDING_SIGNUP_USER_ID_SESSION_KEY] = user.id
        self.request.session[PENDING_SIGNUP_PHONE_SESSION_KEY] = user.username
        messages.success(self.request, _("Verification code sent via SMS."))

        return redirect("signup-verify")


class SignupVerifyView(FormView):
    template_name = "signup_verify.html"
    form_class = OtpVerifyForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return super().dispatch(request, *args, **kwargs)

    def _get_pending(self):
        user_id = self.request.session.get(PENDING_SIGNUP_USER_ID_SESSION_KEY)
        phone = self.request.session.get(PENDING_SIGNUP_PHONE_SESSION_KEY)
        return user_id, phone

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        _user_id, phone = self._get_pending()
        ctx["phone_number"] = phone or ""
        return ctx

    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.utils.translation import gettext as _

        user_id, phone = self._get_pending()
        if not user_id or not phone:
            messages.error(request, _("Please start signup to receive a verification code."))
            return redirect("signup")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        from django.contrib import messages
        from django.contrib.auth import get_user_model
        from django.utils.translation import gettext as _

        from .briq_otp import verify_signup_otp

        User = get_user_model()
        user_id, phone = self._get_pending()

        if not user_id or not phone:
            messages.error(self.request, _("Please start signup to receive a verification code."))
            return redirect("signup")

        user = User.objects.filter(id=user_id, username=phone).first()
        if not user:
            messages.error(self.request, _("Signup session expired. Please sign up again."))
            return redirect("signup")

        ok, err = verify_signup_otp(phone_number=phone, code=form.cleaned_data["code"])
        if not ok:
            form.add_error("code", err or _("Invalid verification code."))
            return self.form_invalid(form)

        user.is_active = True
        user.save(update_fields=["is_active"])
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")

        self.request.session.pop(PENDING_SIGNUP_USER_ID_SESSION_KEY, None)
        self.request.session.pop(PENDING_SIGNUP_PHONE_SESSION_KEY, None)

        messages.success(self.request, _("Phone verified. Your account is now active."))
        return redirect("/members/apply/")


class PasswordResetRequestView(FormView):
    template_name = "password_reset_request.html"
    form_class = PasswordResetRequestForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        from django.contrib import messages
        from django.contrib.auth import get_user_model
        from django.utils.translation import gettext as _

        from .briq_otp import request_signup_otp

        User = get_user_model()
        phone = form.cleaned_data["username"]
        user = User.objects.filter(username=phone, is_active=True).first()
        if not user:
            form.add_error("username", _("No verified account found with this phone number."))
            return self.form_invalid(form)

        ok, err = request_signup_otp(phone_number=phone)
        if not ok:
            logger.error("Password-reset OTP request failed for %s: %s", phone, err)
            form.add_error(None, err or _("Failed to request verification code."))
            return self.form_invalid(form)

        self.request.session[PENDING_PASSWORD_RESET_USER_ID_SESSION_KEY] = user.id
        self.request.session[PENDING_PASSWORD_RESET_PHONE_SESSION_KEY] = phone
        self.request.session[PENDING_PASSWORD_RESET_VERIFIED_SESSION_KEY] = False
        messages.success(self.request, _("Verification code sent via SMS."))
        return redirect("password-reset-verify")


class PasswordResetVerifyView(FormView):
    template_name = "password_reset_verify.html"
    form_class = OtpVerifyForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return super().dispatch(request, *args, **kwargs)

    def _get_pending(self):
        user_id = self.request.session.get(PENDING_PASSWORD_RESET_USER_ID_SESSION_KEY)
        phone = self.request.session.get(PENDING_PASSWORD_RESET_PHONE_SESSION_KEY)
        return user_id, phone

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        _user_id, phone = self._get_pending()
        ctx["phone_number"] = phone or ""
        return ctx

    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.utils.translation import gettext as _

        user_id, phone = self._get_pending()
        if not user_id or not phone:
            messages.error(request, _("Please start password reset first."))
            return redirect("password-reset-request")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        from django.contrib import messages
        from django.contrib.auth import get_user_model
        from django.utils.translation import gettext as _

        from .briq_otp import verify_signup_otp

        User = get_user_model()
        user_id, phone = self._get_pending()
        if not user_id or not phone:
            messages.error(self.request, _("Please start password reset first."))
            return redirect("password-reset-request")

        user = User.objects.filter(id=user_id, username=phone, is_active=True).first()
        if not user:
            messages.error(self.request, _("Password reset session expired. Please try again."))
            return redirect("password-reset-request")

        ok, err = verify_signup_otp(phone_number=phone, code=form.cleaned_data["code"])
        if not ok:
            form.add_error("code", err or _("Invalid verification code."))
            return self.form_invalid(form)

        self.request.session[PENDING_PASSWORD_RESET_VERIFIED_SESSION_KEY] = True
        return redirect("password-reset-set")


class PasswordResetSetView(FormView):
    template_name = "password_reset_set.html"
    form_class = PasswordResetSetForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return super().dispatch(request, *args, **kwargs)

    def _can_set_password(self):
        user_id = self.request.session.get(PENDING_PASSWORD_RESET_USER_ID_SESSION_KEY)
        phone = self.request.session.get(PENDING_PASSWORD_RESET_PHONE_SESSION_KEY)
        verified = self.request.session.get(PENDING_PASSWORD_RESET_VERIFIED_SESSION_KEY)
        return user_id, phone, bool(verified)

    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.utils.translation import gettext as _

        user_id, phone, verified = self._can_set_password()
        if not user_id or not phone or not verified:
            messages.error(request, _("Please verify OTP before setting a new password."))
            return redirect("password-reset-request")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        from django.contrib import messages
        from django.contrib.auth import get_user_model
        from django.utils.translation import gettext as _

        User = get_user_model()
        user_id, phone, verified = self._can_set_password()
        if not user_id or not phone or not verified:
            messages.error(self.request, _("Please verify OTP before setting a new password."))
            return redirect("password-reset-request")

        user = User.objects.filter(id=user_id, username=phone, is_active=True).first()
        if not user:
            messages.error(self.request, _("Password reset session expired. Please try again."))
            return redirect("password-reset-request")

        user.set_password(form.cleaned_data["password1"])
        user.save(update_fields=["password"])
        self.request.session.pop(PENDING_PASSWORD_RESET_USER_ID_SESSION_KEY, None)
        self.request.session.pop(PENDING_PASSWORD_RESET_PHONE_SESSION_KEY, None)
        self.request.session.pop(PENDING_PASSWORD_RESET_VERIFIED_SESSION_KEY, None)
        messages.success(self.request, _("Password updated successfully. Please sign in."))
        return redirect("login")


class CustomLoginView(LoginView):
    template_name = "login.html"
    authentication_form = PhoneLoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        self.request.session["user_id"] = user.id
        self.request.session["user_name"] = user.get_username()
        return response

    def get_success_url(self):
        user = self.request.user
        tenant = getattr(self.request, "tenant", None)
        is_admin = user.is_superuser or user.id == 1
        if tenant and not is_admin:
            member = Member.objects.filter(tenant=tenant, username=user.username).first()
            if not member:
                application = MemberApplication.objects.filter(
                    tenant=tenant, user=user
                ).first()
                if application and application.status == MemberApplication.STATUS_PENDING:
                    return reverse("members:apply-submitted")
                return reverse("members:apply")
        return super().get_success_url()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            ctx["tenant"] = tenant
            ctx["recent_announcements"] = Announcement.objects.filter(
                tenant=tenant, is_active=True
            )[:5]

        is_admin = self.request.user.is_superuser or self.request.user.id == 1
        member = None
        if tenant:
            member = Member.objects.filter(
                tenant=tenant, username=self.request.user.username
            ).first()

        if tenant and is_admin:
            ctx["member_count"] = Member.objects.filter(tenant=tenant).count()
            ctx["fellowship_count"] = FellowshipGroup.objects.filter(
                tenant=tenant
            ).count()
            ctx["pledge_count"] = Pledge.objects.filter(tenant=tenant).count()
            ctx["pending_applications"] = MemberApplication.objects.filter(
                tenant=tenant, status=MemberApplication.STATUS_PENDING
            ).count()
        else:
            ctx["member_full_name"] = member.full_name if member else None
            ctx["member_count"] = 1 if member else 0
            ctx["pledge_count"] = (
                Pledge.objects.filter(tenant=tenant, member=member).count()
                if tenant and member
                else 0
            )
            participation = None
            if member:
                participation = (
                    FellowshipParticipation.objects.select_related("group")
                    .filter(tenant=tenant, member=member)
                    .first()
                )
            ctx["fellowship_count"] = 1 if participation else 0
            if participation:
                group = participation.group
                ctx["member_fellowship"] = group
                ctx["fellowship_members"] = (
                    FellowshipParticipation.objects.select_related("member")
                    .filter(tenant=tenant, group=group)
                    .order_by("member__full_name")
                )
            else:
                ctx["member_fellowship"] = None
        return ctx


class TenantCreateView(LoginRequiredMixin, CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = "tenants/create.html"
    success_url = reverse_lazy("home")


def logout_view(request):
    logout(request)
    return redirect(getattr(settings, "LOGOUT_REDIRECT_URL", "/") or "/")


 
