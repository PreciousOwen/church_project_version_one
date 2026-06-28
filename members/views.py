import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    MemberForm,
    MemberApplicationApprovalForm,
    MemberApplicationForm,
    MemberApplicationStep1Form,
    MemberApplicationStep2Form,
    MemberApplicationStep3Form,
    MemberApplicationStep4Form,
    MemberApplicationStep5Form,
    MemberApplicationStep6Form,
    MemberStep1Form,
    MemberStep2Form,
    MemberStep3Form,
    MemberStep4Form,
    MemberStep5Form,
    MemberStep6Form,
    SpiritualProgressForm,
)
from .models import Member, MemberApplication, SpiritualProgress
from pledges.models import Pledge

WIZARD_SESSION_KEY = "member_wizard_data"
APPLICATION_WIZARD_SESSION_KEY = "member_application_wizard_data"
WIZARD_STEPS = {
    1: ("Personal information", MemberStep1Form),
    2: ("Contacts and residence", MemberStep2Form),
    3: ("Education, profession, and occupation", MemberStep3Form),
    4: ("Spiritual services", MemberStep4Form),
    5: ("Participation in congregation services", MemberStep5Form),
    6: ("Fellowship and service interest", MemberStep6Form),
}
APPLICATION_WIZARD_STEPS = {
    1: ("Personal information", MemberApplicationStep1Form),
    2: ("Contacts and residence", MemberApplicationStep2Form),
    3: ("Education, profession, and occupation", MemberApplicationStep3Form),
    4: ("Spiritual services", MemberApplicationStep4Form),
    5: ("Participation in congregation services", MemberApplicationStep5Form),
    6: ("Fellowship and service interest", MemberApplicationStep6Form),
}
FIELD_STEP_MAP = {
    "membership_no": 1,
    "full_name": 1,
    "gender": 1,
    "dob": 1,
    "place_of_birth": 1,
    "marital_status": 1,
    "marriage_type": 1,
    "marriage_date": 1,
    "marriage_place": 1,
    "spouse_name": 1,
    "living_with_spouse_name": 1,
    "dependents": 1,
    "primary_phone": 2,
    "spouse_phone": 2,
    "email": 2,
    "po_box": 2,
    "house_number": 2,
    "residence_name": 2,
    "block_number": 2,
    "previous_parish": 2,
    "fellowship_name": 2,
    "neighbor_name": 2,
    "neighbor_phone": 2,
    "elder_name": 2,
    "elder_phone": 2,
    "occupation": 3,
    "work_place": 3,
    "education_level": 3,
    "profession": 3,
    "volunteer_status": 3,
    "is_baptized": 4,
    "baptism_date": 4,
    "is_confirmed": 4,
    "confirmation_date": 4,
    "participates_in_sacraments": 4,
    "participates_in_fellowship": 5,
    "fellowship_house_name": 5,
    "fellowship_non_participation_reason": 5,
    "fellowship_chairperson_name": 5,
    "fellowship_chairperson_signature": 5,
    "join_fellowship": 6,
    "join_sunday_school": 6,
    "join_visiting_sick": 6,
    "join_bible_study": 6,
    "join_choir": 6,
    "join_union": 6,
    "password": 6,
}
APPLICATION_FIELD_STEP_MAP = {
    "full_name": 1,
    "gender": 1,
    "dob": 1,
    "place_of_birth": 1,
    "marital_status": 1,
    "marriage_type": 1,
    "marriage_date": 1,
    "marriage_place": 1,
    "spouse_name": 1,
    "living_with_spouse_name": 1,
    "dependents": 1,
    "primary_phone": 2,
    "spouse_phone": 2,
    "email": 2,
    "po_box": 2,
    "house_number": 2,
    "residence_name": 2,
    "block_number": 2,
    "previous_parish": 2,
    "fellowship_name": 2,
    "neighbor_name": 2,
    "neighbor_phone": 2,
    "elder_name": 2,
    "elder_phone": 2,
    "occupation": 3,
    "work_place": 3,
    "education_level": 3,
    "profession": 3,
    "volunteer_status": 3,
    "is_baptized": 4,
    "baptism_date": 4,
    "is_confirmed": 4,
    "confirmation_date": 4,
    "participates_in_sacraments": 4,
    "participates_in_fellowship": 5,
    "fellowship_house_name": 5,
    "fellowship_non_participation_reason": 5,
    "fellowship_chairperson_name": 5,
    "fellowship_chairperson_signature": 5,
    "join_fellowship": 6,
    "join_sunday_school": 6,
    "join_visiting_sick": 6,
    "join_bible_study": 6,
    "join_choir": 6,
    "join_union": 6,
    "pledge_year": 6,
    "pledge_building": 6,
    "pledge_stewardship": 6,
    "pledge_other": 6,
    "has_membership_number": 6,
    "membership_number": 6,
    "membership_registration_date": 6,
    "membership_registered_full_name": 6,
}


def _serialize_value(value):
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return value
    if value is None:
        return ""
    return value


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
        tenant = self.get_tenant()
        if tenant is None:
            form.add_error(None, "Tenant is not set. Create a tenant or provide the tenant header.")
            return self.form_invalid(form)
        if hasattr(form, "instance"):
            form.instance.tenant = tenant
        return super().form_valid(form)


class MemberListView(TenantMixin, ListView):
    model = Member
    template_name = "members/list.html"
    context_object_name = "members"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.is_admin():
            return qs.filter(username=self.request.user.username)
        q = self.request.GET.get("q", "")
        if q:
            qs = qs.filter(full_name__icontains=q) | qs.filter(
                membership_no__icontains=q
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_query"] = self.request.GET.get("q", "")
        return ctx


class MemberDetailView(TenantMixin, DetailView):
    model = Member
    template_name = "members/detail.html"
    context_object_name = "member"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx["spiritual_progress"] = self.object.spiritual_progress
        except SpiritualProgress.DoesNotExist:
            ctx["spiritual_progress"] = None
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.is_admin():
            return qs.filter(username=self.request.user.username)
        return qs


class MemberProfileView(TenantMixin, TemplateView):
    template_name = "members/me.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tenant = self.get_tenant()
        member = None
        application = None

        if tenant is not None:
            member = Member.objects.filter(
                tenant=tenant,
                username=self.request.user.username,
            ).first()
            application = MemberApplication.objects.filter(
                tenant=tenant,
                user=self.request.user,
            ).first()

        ctx["member"] = member
        ctx["application"] = application
        ctx["profile_state"] = "approved" if member else "not_approved"

        if member:
            try:
                ctx["spiritual_progress"] = member.spiritual_progress
            except SpiritualProgress.DoesNotExist:
                ctx["spiritual_progress"] = None
        else:
            ctx["spiritual_progress"] = None

        return ctx


class MemberCreateView(TenantMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = "members/form.html"
    success_url = reverse_lazy("members:list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Add New Member"
        return ctx

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Member added successfully.")
        return super().form_valid(form)


class MemberUpdateView(TenantMixin, UpdateView):
    model = Member
    form_class = MemberForm
    template_name = "members/form.html"

    def get_success_url(self):
        return reverse_lazy("members:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Edit {self.object.full_name}"
        ctx["can_change_login_password"] = bool(self.object.username)
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Member updated successfully.")
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if request.POST.get("action") == "reset-member-password":
            return self._handle_password_reset(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def _handle_password_reset(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied

        self.object = self.get_object()
        password1 = (request.POST.get("password1") or "").strip()
        password2 = (request.POST.get("password2") or "").strip()

        if not password1 or not password2:
            messages.error(request, "Enter and confirm the new password.")
            return redirect("members:update", pk=self.object.pk)
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("members:update", pk=self.object.pk)
        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 digits long.")
            return redirect("members:update", pk=self.object.pk)
        if not password1.isdigit():
            messages.error(request, "Password must contain digits only.")
            return redirect("members:update", pk=self.object.pk)

        User = get_user_model()
        user = User.objects.filter(username=self.object.username).first()
        if not user:
            messages.error(request, "No login account found for this member.")
            return redirect("members:update", pk=self.object.pk)

        user.set_password(password1)
        user.save(update_fields=["password"])
        messages.success(request, f"Password changed for {self.object.full_name}.")
        return redirect("members:update", pk=self.object.pk)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MemberDeleteView(TenantMixin, DeleteView):
    model = Member
    template_name = "members/confirm_delete.html"
    success_url = reverse_lazy("members:list")

    def form_valid(self, form):
        messages.success(self.request, "Member deleted.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SpiritualProgressView(LoginRequiredMixin, UpdateView):
    model = SpiritualProgress
    form_class = SpiritualProgressForm
    template_name = "members/spiritual_progress_form.html"

    def get_object(self, queryset=None):
        member = get_object_or_404(Member, pk=self.kwargs["member_pk"])
        obj, _ = SpiritualProgress.objects.get_or_create(
            member=member, defaults={"tenant": member.tenant}
        )
        return obj

    def get_success_url(self):
        return reverse_lazy("members:detail", kwargs={"pk": self.kwargs["member_pk"]})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["member"] = get_object_or_404(Member, pk=self.kwargs["member_pk"])
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Spiritual progress updated.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.id == 1):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MemberWizardStepView(TenantMixin, FormView):
    template_name = "members/wizard_step.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        step = int(self.kwargs.get("step", 1))
        if step not in WIZARD_STEPS:
            return redirect("members:create")
        if step == 1 and request.method == "GET":
            request.session.pop(WIZARD_SESSION_KEY, None)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        _, form_class = WIZARD_STEPS[int(self.kwargs.get("step", 1))]
        return form_class

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get(WIZARD_SESSION_KEY, {})
        initial.update(data)
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        step = int(self.kwargs.get("step", 1))
        title, _ = WIZARD_STEPS[step]
        ctx["title"] = title
        ctx["step"] = step
        ctx["total_steps"] = len(WIZARD_STEPS)
        if step > 1:
            ctx["prev_url"] = reverse_lazy("members:create-step", kwargs={"step": step - 1})
        if step < len(WIZARD_STEPS):
            ctx["next_url"] = reverse_lazy("members:create-step", kwargs={"step": step + 1})
        return ctx

    def form_valid(self, form):
        step = int(self.kwargs.get("step", 1))
        data = self.request.session.get(WIZARD_SESSION_KEY, {})
        for key, value in form.cleaned_data.items():
            data[key] = _serialize_value(value)
        self.request.session[WIZARD_SESSION_KEY] = data
        self.request.session.modified = True

        if step < len(WIZARD_STEPS):
            return redirect("members:create-step", step=step + 1)

        final_form = MemberForm(data)
        if final_form.is_valid():
            member = final_form.save(commit=False)
            member.tenant = self.get_tenant()
            member.save()
            messages.success(self.request, "Member added successfully.")
            self.request.session.pop(WIZARD_SESSION_KEY, None)
            return redirect("members:list")

        error_field = next(iter(final_form.errors.keys()), None)
        target_step = FIELD_STEP_MAP.get(error_field, 1)
        messages.error(self.request, "Please review the highlighted fields and try again.")
        return redirect("members:create-step", step=target_step)


class MemberApplicationWizardStepView(TenantMixin, FormView):
    template_name = "members/wizard_step.html"

    def dispatch(self, request, *args, **kwargs):
        step = int(self.kwargs.get("step", 1))
        if step not in APPLICATION_WIZARD_STEPS:
            return redirect("members:apply")
        if step == 1 and request.method == "GET":
            request.session.pop(APPLICATION_WIZARD_SESSION_KEY, None)
        if self.get_member():
            return redirect("members:me")
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        _, form_class = APPLICATION_WIZARD_STEPS[int(self.kwargs.get("step", 1))]
        return form_class

    def get_initial(self):
        initial = super().get_initial()
        data = self.request.session.get(APPLICATION_WIZARD_SESSION_KEY, {})
        initial.update(data)
        if not initial.get("primary_phone") and self.request.user.is_authenticated:
            initial["primary_phone"] = self.request.user.get_username()
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        step = int(self.kwargs.get("step", 1))
        title, _ = APPLICATION_WIZARD_STEPS[step]
        ctx["title"] = title
        ctx["step"] = step
        ctx["total_steps"] = len(APPLICATION_WIZARD_STEPS)
        ctx["application_mode"] = True
        ctx["hide_sidebar"] = True
        ctx["show_lang_switcher_top"] = True
        if step > 1:
            ctx["prev_url"] = reverse_lazy("members:apply-step", kwargs={"step": step - 1})
        if step < len(APPLICATION_WIZARD_STEPS):
            ctx["next_url"] = reverse_lazy("members:apply-step", kwargs={"step": step + 1})
        return ctx

    def form_valid(self, form):
        step = int(self.kwargs.get("step", 1))
        data = self.request.session.get(APPLICATION_WIZARD_SESSION_KEY, {})
        for key, value in form.cleaned_data.items():
            data[key] = _serialize_value(value)
        self.request.session[APPLICATION_WIZARD_SESSION_KEY] = data
        self.request.session.modified = True

        if step < len(APPLICATION_WIZARD_STEPS):
            return redirect("members:apply-step", step=step + 1)

        final_form = MemberApplicationForm(data)
        if final_form.is_valid():
            tenant = self.get_tenant()
            if tenant is None:
                messages.error(self.request, "Tenant is not set. Please contact support.")
                return redirect("members:apply")
            defaults = dict(final_form.cleaned_data)
            if not defaults.get("primary_phone"):
                defaults["primary_phone"] = self.request.user.get_username()
            defaults.update(
                {
                    "status": MemberApplication.STATUS_PENDING,
                    "reviewed_by": None,
                    "reviewed_at": None,
                }
            )
            application, _ = MemberApplication.objects.update_or_create(
                tenant=tenant,
                user=self.request.user,
                defaults=defaults,
            )
            messages.success(self.request, "Your application has been submitted for approval.")
            self.request.session.pop(APPLICATION_WIZARD_SESSION_KEY, None)
            return redirect("members:apply-submitted")

        error_field = next(iter(final_form.errors.keys()), None)
        target_step = APPLICATION_FIELD_STEP_MAP.get(error_field, 1)
        messages.error(self.request, "Please review the highlighted fields and try again.")
        return redirect("members:apply-step", step=target_step)


class MemberApplicationSubmittedView(TenantMixin, TemplateView):
    template_name = "members/application_submitted.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["hide_sidebar"] = True
        ctx["show_lang_switcher_top"] = True
        return ctx


class MemberApplicationListView(TenantMixin, ListView):
    model = MemberApplication
    template_name = "members/applications_list.html"
    context_object_name = "applications"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = self.get_tenant()
        if tenant is None:
            return qs.none()
        status = self.request.GET.get("status")
        qs = qs.filter(tenant=tenant)
        if status:
            qs = qs.filter(status=status)
        return qs


class MemberApplicationApproveView(TenantMixin, FormView):
    template_name = "members/application_approve.html"
    form_class = MemberApplicationApprovalForm

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_application(self):
        tenant = self.get_tenant()
        return get_object_or_404(
            MemberApplication,
            pk=self.kwargs["pk"],
            tenant=tenant,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["application"] = self.get_application()
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.get_tenant()
        kwargs["application"] = self.get_application()
        return kwargs

    def form_valid(self, form):
        application = self.get_application()
        membership_no = form.cleaned_data["membership_no"].strip()
        tenant = self.get_tenant()

        member_for_username = Member.objects.filter(
            tenant=tenant,
            username=application.user.username,
        ).first()
        member_for_membership = Member.objects.filter(
            tenant=tenant,
            membership_no=membership_no,
        ).first()

        if (
            application.has_membership_number
            and member_for_membership
            and (not member_for_username or member_for_username.pk == member_for_membership.pk)
        ):
            member = member_for_membership
        elif member_for_username:
            member = member_for_username
        else:
            member = Member(tenant=tenant, username=application.user.username)

        member.username = application.user.username
        member.membership_no = membership_no
        member.full_name = application.full_name
        member.gender = application.gender
        member.dob = application.dob
        member.place_of_birth = application.place_of_birth
        member.marital_status = application.marital_status
        member.marriage_type = application.marriage_type
        member.marriage_date = application.marriage_date
        member.marriage_place = application.marriage_place
        member.spouse_name = application.spouse_name
        member.living_with_spouse_name = application.living_with_spouse_name
        member.dependents = application.dependents
        member.primary_phone = application.primary_phone
        member.spouse_phone = application.spouse_phone
        member.email = application.email
        member.po_box = application.po_box
        member.house_number = application.house_number
        member.residence_name = application.residence_name
        member.block_number = application.block_number
        member.fellowship_name = application.fellowship_name
        member.previous_parish = application.previous_parish
        member.neighbor_name = application.neighbor_name
        member.neighbor_phone = application.neighbor_phone
        member.elder_name = application.elder_name
        member.elder_phone = application.elder_phone
        member.occupation = application.occupation
        member.work_place = application.work_place
        member.education_level = application.education_level
        member.profession = application.profession
        member.volunteer_status = application.volunteer_status
        member.is_baptized = application.is_baptized
        member.baptism_date = application.baptism_date
        member.is_confirmed = application.is_confirmed
        member.confirmation_date = application.confirmation_date
        member.participates_in_sacraments = application.participates_in_sacraments
        member.participates_in_fellowship = application.participates_in_fellowship
        member.fellowship_house_name = application.fellowship_house_name
        member.fellowship_non_participation_reason = application.fellowship_non_participation_reason
        member.fellowship_chairperson_name = application.fellowship_chairperson_name
        member.fellowship_chairperson_signature = application.fellowship_chairperson_signature
        member.join_fellowship = application.join_fellowship
        member.join_sunday_school = application.join_sunday_school
        member.join_visiting_sick = application.join_visiting_sick
        member.join_bible_study = application.join_bible_study
        member.join_choir = application.join_choir
        member.join_union = application.join_union
        member.pledge_year = application.pledge_year
        member.pledge_building = application.pledge_building
        member.pledge_stewardship = application.pledge_stewardship
        member.pledge_other = application.pledge_other
        member.has_membership_number = application.has_membership_number
        member.membership_registration_date = application.membership_registration_date
        member.membership_registered_full_name = application.membership_registered_full_name
        member.save()

        application.status = MemberApplication.STATUS_APPROVED
        application.assigned_membership_no = membership_no
        application.reviewed_by = self.request.user
        application.reviewed_at = timezone.now()
        application.save()

        pledge_year = application.pledge_year or 0
        if pledge_year:
            pledge_building = application.pledge_building or Decimal("0")
            pledge_stewardship = application.pledge_stewardship or Decimal("0")
            pledge_other = application.pledge_other or Decimal("0")
            if any(value > 0 for value in (pledge_building, pledge_stewardship, pledge_other)):
                Pledge.objects.update_or_create(
                    tenant=tenant,
                    member=member,
                    year=pledge_year,
                    defaults={
                        "building_pledge": pledge_building,
                        "stewardship_pledge": pledge_stewardship,
                        "other_pledges": pledge_other,
                    },
                )

        messages.success(self.request, "Application approved and membership assigned.")
        return redirect("members:applications")
