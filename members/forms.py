from decimal import Decimal, InvalidOperation

from django import forms
from django.forms.utils import pretty_name
from django.utils.translation import gettext_lazy as _

from .models import Member, MemberApplication, SpiritualProgress

GENDER_CHOICES = [("Male", _("Male")), ("Female", _("Female"))]
MARITAL_CHOICES = [
    ("Single", _("Single")),
    ("Married", _("Married")),
    ("Widowed", _("Widowed")),
    ("Divorced", _("Divorced")),
]
MARRIAGE_TYPE_CHOICES = [
    ("----------", _("----------")),
    ("Church", _("Church")),
    ("Traditional", _("Traditional")),
    ("Civil", _("Civil")),
]
EDUCATION_CHOICES = [
    ("Primary", _("Primary")),
    ("Secondary", _("Secondary")),
    ("Certificate", _("Certificate")),
    ("Diploma", _("Diploma")),
    ("Degree", _("Degree")),
    ("Masters", _("Masters")),
    ("PhD", _("PhD")),
]


class MemberForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    marital_status = forms.ChoiceField(choices=MARITAL_CHOICES)
    marriage_type = forms.ChoiceField(choices=MARRIAGE_TYPE_CHOICES, required=False)
    dob = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    marriage_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    dependents = forms.JSONField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": _(
                    "[{\"full_name\": \"John Doe\", \"dob\": \"2010-05-01\", \"relationship\": \"Son\"}]"
                ),
            }
        ),
        help_text=_(
            "Enter a JSON list of dependents with full_name, dob, and relationship."
        ),
    )
    education_level = forms.ChoiceField(
        choices=[("", _("---------"))] + EDUCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    volunteer_status = forms.TypedChoiceField(
        choices=[("True", _("Yes")), ("False", _("No"))],
        required=False,
        coerce=lambda value: value == "True",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Member
        fields = [
            "membership_no",
            "full_name",
            "gender",
            "dob",
            "place_of_birth",
            "marital_status",
            "marriage_type",
            "marriage_date",
            "marriage_place",
            "spouse_name",
            "living_with_spouse_name",
            "dependents",
            "primary_phone",
            "spouse_phone",
            "email",
            "po_box",
            "house_number",
            "residence_name",
            "block_number",
            "previous_parish",
            "fellowship_name",
            "neighbor_name",
            "neighbor_phone",
            "elder_name",
            "elder_phone",
            "occupation",
            "work_place",
            "education_level",
            "profession",
            "volunteer_status",
            "is_baptized",
            "baptism_date",
            "is_confirmed",
            "confirmation_date",
            "participates_in_sacraments",
            "participates_in_fellowship",
            "fellowship_house_name",
            "fellowship_non_participation_reason",
            "fellowship_chairperson_name",
            "fellowship_chairperson_signature",
            "join_fellowship",
            "join_sunday_school",
            "join_visiting_sick",
            "join_bible_study",
            "join_choir",
            "join_union",
            "password",
        ]
        widgets = {
            "membership_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
            "marital_status": forms.Select(attrs={"class": "form-select"}),
            "marriage_type": forms.Select(attrs={"class": "form-select"}),
            "marriage_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "marriage_place": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_name": forms.TextInput(attrs={"class": "form-control"}),
            "living_with_spouse_name": forms.TextInput(attrs={"class": "form-control"}),
            "primary_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "spouse_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "po_box": forms.TextInput(
                attrs={
                    "class": "form-control input-number",
                    "inputmode": "numeric",
                    "data-cleave": "number",
                    "data-decimal": "false",
                }
            ),
            "house_number": forms.TextInput(
                attrs={
                    "class": "form-control input-number",
                    "inputmode": "numeric",
                    "data-cleave": "number",
                    "data-decimal": "false",
                }
            ),
            "residence_name": forms.TextInput(attrs={"class": "form-control"}),
            "block_number": forms.TextInput(
                attrs={
                    "class": "form-control input-number",
                    "inputmode": "numeric",
                    "data-cleave": "number",
                    "data-decimal": "false",
                }
            ),
            "previous_parish": forms.TextInput(attrs={"class": "form-control"}),
            "fellowship_name": forms.TextInput(attrs={"class": "form-control"}),
            "neighbor_name": forms.TextInput(attrs={"class": "form-control"}),
            "neighbor_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "elder_name": forms.TextInput(attrs={"class": "form-control"}),
            "elder_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "occupation": forms.TextInput(attrs={"class": "form-control"}),
            "work_place": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "baptism_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "confirmation_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fellowship_house_name": forms.TextInput(attrs={"class": "form-control"}),
            "fellowship_non_participation_reason": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "fellowship_chairperson_name": forms.TextInput(attrs={"class": "form-control"}),
            "fellowship_chairperson_signature": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].required = False

        label_overrides = {
            "dob": "Date of birth",
        }

        for name, field in self.fields.items():
            if not field.label:
                field.label = _(label_overrides.get(name, pretty_name(name)))
            elif isinstance(field.label, str):
                field.label = _(field.label)

            if isinstance(field.help_text, str) and field.help_text:
                field.help_text = _(field.help_text)

            placeholder = field.widget.attrs.get("placeholder")
            if isinstance(placeholder, str) and placeholder:
                field.widget.attrs["placeholder"] = _(placeholder)


class MemberApplicationForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    marital_status = forms.ChoiceField(choices=MARITAL_CHOICES)
    marriage_type = forms.ChoiceField(choices=MARRIAGE_TYPE_CHOICES, required=False)
    dob = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    marriage_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    dependents = forms.JSONField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": _(
                    "[{\"full_name\": \"John Doe\", \"dob\": \"2010-05-01\", \"relationship\": \"Son\"}]"
                ),
            }
        ),
        help_text=_(
            "Enter a JSON list of dependents with full_name, dob, and relationship."
        ),
    )
    education_level = forms.ChoiceField(
        choices=[("", _("---------"))] + EDUCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    volunteer_status = forms.TypedChoiceField(
        choices=[("True", _("Yes")), ("False", _("No"))],
        required=False,
        coerce=lambda value: value == "True",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    pledge_year = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control input-number",
                "inputmode": "numeric",
                "data-cleave": "number",
                "data-decimal": "false",
            }
        ),
    )
    pledge_building = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control input-number",
                "inputmode": "decimal",
                "data-cleave": "number",
                "data-decimal": "true",
            }
        ),
    )
    pledge_stewardship = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control input-number",
                "inputmode": "decimal",
                "data-cleave": "number",
                "data-decimal": "true",
            }
        ),
    )
    pledge_other = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control input-number",
                "inputmode": "decimal",
                "data-cleave": "number",
                "data-decimal": "true",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        label_overrides = {
            "dob": "Date of birth",
        }

        for name, field in self.fields.items():
            if not field.label:
                field.label = _(label_overrides.get(name, pretty_name(name)))
            elif isinstance(field.label, str):
                field.label = _(field.label)

            if isinstance(field.help_text, str) and field.help_text:
                field.help_text = _(field.help_text)

            placeholder = field.widget.attrs.get("placeholder")
            if isinstance(placeholder, str) and placeholder:
                field.widget.attrs["placeholder"] = _(placeholder)

    class Meta:
        model = MemberApplication
        fields = [
            "full_name",
            "gender",
            "dob",
            "place_of_birth",
            "marital_status",
            "marriage_type",
            "marriage_date",
            "marriage_place",
            "spouse_name",
            "living_with_spouse_name",
            "dependents",
            "primary_phone",
            "spouse_phone",
            "email",
            "po_box",
            "house_number",
            "residence_name",
            "block_number",
            "previous_parish",
            "fellowship_name",
            "neighbor_name",
            "neighbor_phone",
            "elder_name",
            "elder_phone",
            "occupation",
            "work_place",
            "education_level",
            "profession",
            "volunteer_status",
            "is_baptized",
            "baptism_date",
            "is_confirmed",
            "confirmation_date",
            "participates_in_sacraments",
            "participates_in_fellowship",
            "fellowship_house_name",
            "fellowship_non_participation_reason",
            "fellowship_chairperson_name",
            "fellowship_chairperson_signature",
            "join_fellowship",
            "join_sunday_school",
            "join_visiting_sick",
            "join_bible_study",
            "join_choir",
            "join_union",
            "pledge_year",
            "pledge_building",
            "pledge_stewardship",
            "pledge_other",
            "has_membership_number",
            "membership_number",
            "membership_registration_date",
            "membership_registered_full_name",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "dob": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "place_of_birth": forms.TextInput(attrs={"class": "form-control"}),
            "marital_status": forms.Select(attrs={"class": "form-select"}),
            "marriage_type": forms.Select(attrs={"class": "form-select"}),
            "marriage_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "marriage_place": forms.TextInput(attrs={"class": "form-control"}),
            "spouse_name": forms.TextInput(attrs={"class": "form-control"}),
            "living_with_spouse_name": forms.TextInput(attrs={"class": "form-control"}),
            "primary_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "spouse_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "po_box": forms.TextInput(
                attrs={
                    "class": "form-control input-number",
                    "inputmode": "numeric",
                    "data-cleave": "number",
                    "data-decimal": "false",
                }
            ),
            "house_number": forms.TextInput(
                attrs={
                    "class": "form-control input-number",
                    "inputmode": "numeric",
                    "data-cleave": "number",
                    "data-decimal": "false",
                }
            ),
            "residence_name": forms.TextInput(attrs={"class": "form-control"}),
            "block_number": forms.TextInput(
                attrs={
                    "class": "form-control input-number",
                    "inputmode": "numeric",
                    "data-cleave": "number",
                    "data-decimal": "false",
                }
            ),
            "previous_parish": forms.TextInput(attrs={"class": "form-control"}),
            "fellowship_name": forms.TextInput(attrs={"class": "form-control"}),
            "neighbor_name": forms.TextInput(attrs={"class": "form-control"}),
            "neighbor_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "elder_name": forms.TextInput(attrs={"class": "form-control"}),
            "elder_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "tel",
                }
            ),
            "occupation": forms.TextInput(attrs={"class": "form-control"}),
            "work_place": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "baptism_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "confirmation_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fellowship_house_name": forms.TextInput(attrs={"class": "form-control"}),
            "fellowship_non_participation_reason": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "fellowship_chairperson_name": forms.TextInput(attrs={"class": "form-control"}),
            "fellowship_chairperson_signature": forms.TextInput(attrs={"class": "form-control"}),
            "has_membership_number": forms.Select(
                attrs={"class": "form-select"},
                choices=[(False, _("No")), (True, _("Yes"))],
            ),
            "membership_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "membership_registration_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "membership_registered_full_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }

    def _parse_decimal(self, value):
        if value in (None, ""):
            return Decimal("0")
        try:
            return Decimal(str(value).replace(",", ""))
        except (InvalidOperation, ValueError):
            raise forms.ValidationError(_("Enter a valid number."))

    def clean_pledge_year(self):
        value = self.cleaned_data.get("pledge_year")
        if value in (None, ""):
            return 0
        try:
            return int(str(value).replace(",", ""))
        except (TypeError, ValueError):
            raise forms.ValidationError(_("Enter a valid year."))

    def clean_pledge_building(self):
        return self._parse_decimal(self.cleaned_data.get("pledge_building"))

    def clean_pledge_stewardship(self):
        return self._parse_decimal(self.cleaned_data.get("pledge_stewardship"))

    def clean_pledge_other(self):
        return self._parse_decimal(self.cleaned_data.get("pledge_other"))

    def clean(self):
        cleaned = super().clean()
        has_membership_number = cleaned.get("has_membership_number")
        membership_number = (cleaned.get("membership_number") or "").strip()
        registration_date = cleaned.get("membership_registration_date")
        registered_name = (cleaned.get("membership_registered_full_name") or "").strip()
        if has_membership_number:
            if not membership_number:
                self.add_error(
                    "membership_number",
                    _("Enter the membership number."),
                )
            if not registration_date:
                self.add_error(
                    "membership_registration_date",
                    _("Enter the registration date."),
                )
            if not registered_name:
                self.add_error(
                    "membership_registered_full_name",
                    _("Enter the full name used during registration."),
                )
        else:
            cleaned["membership_number"] = ""
        return cleaned


def _prune_step_fields(form):
    allowed = set(form._meta.fields or [])
    for name in list(form.fields.keys()):
        if name not in allowed:
            form.fields.pop(name, None)


class MemberStep1Form(MemberForm):
    class Meta(MemberForm.Meta):
        fields = [
            "membership_no",
            "full_name",
            "gender",
            "dob",
            "place_of_birth",
            "marital_status",
            "marriage_type",
            "marriage_date",
            "marriage_place",
            "spouse_name",
            "living_with_spouse_name",
            "dependents",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberStep2Form(MemberForm):
    class Meta(MemberForm.Meta):
        fields = [
            "primary_phone",
            "spouse_phone",
            "email",
            "po_box",
            "house_number",
            "residence_name",
            "block_number",
            "previous_parish",
            "fellowship_name",
            "neighbor_name",
            "neighbor_phone",
            "elder_name",
            "elder_phone",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberStep3Form(MemberForm):
    class Meta(MemberForm.Meta):
        fields = [
            "occupation",
            "work_place",
            "education_level",
            "profession",
            "volunteer_status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberStep4Form(MemberForm):
    class Meta(MemberForm.Meta):
        fields = [
            "is_baptized",
            "baptism_date",
            "is_confirmed",
            "confirmation_date",
            "participates_in_sacraments",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberStep5Form(MemberForm):
    class Meta(MemberForm.Meta):
        fields = [
            "participates_in_fellowship",
            "fellowship_house_name",
            "fellowship_non_participation_reason",
            "fellowship_chairperson_name",
            "fellowship_chairperson_signature",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberStep6Form(MemberForm):
    class Meta(MemberForm.Meta):
        fields = [
            "join_fellowship",
            "join_sunday_school",
            "join_visiting_sick",
            "join_bible_study",
            "join_choir",
            "join_union",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberApplicationStep1Form(MemberApplicationForm):
    class Meta(MemberApplicationForm.Meta):
        fields = [
            "full_name",
            "gender",
            "dob",
            "place_of_birth",
            "marital_status",
            "marriage_type",
            "marriage_date",
            "marriage_place",
            "spouse_name",
            "living_with_spouse_name",
            "dependents",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberApplicationStep2Form(MemberApplicationForm):
    class Meta(MemberApplicationForm.Meta):
        fields = [
            "primary_phone",
            "spouse_phone",
            "email",
            "po_box",
            "house_number",
            "residence_name",
            "block_number",
            "previous_parish",
            "fellowship_name",
            "neighbor_name",
            "neighbor_phone",
            "elder_name",
            "elder_phone",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberApplicationStep3Form(MemberApplicationForm):
    class Meta(MemberApplicationForm.Meta):
        fields = [
            "occupation",
            "work_place",
            "education_level",
            "profession",
            "volunteer_status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberApplicationStep4Form(MemberApplicationForm):
    class Meta(MemberApplicationForm.Meta):
        fields = [
            "is_baptized",
            "baptism_date",
            "is_confirmed",
            "confirmation_date",
            "participates_in_sacraments",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberApplicationStep5Form(MemberApplicationForm):
    class Meta(MemberApplicationForm.Meta):
        fields = [
            "participates_in_fellowship",
            "fellowship_house_name",
            "fellowship_non_participation_reason",
            "fellowship_chairperson_name",
            "fellowship_chairperson_signature",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberApplicationStep6Form(MemberApplicationForm):
    class Meta(MemberApplicationForm.Meta):
        fields = [
            "join_fellowship",
            "join_sunday_school",
            "join_visiting_sick",
            "join_bible_study",
            "join_choir",
            "join_union",
            "pledge_year",
            "pledge_building",
            "pledge_stewardship",
            "pledge_other",
            "has_membership_number",
            "membership_number",
            "membership_registration_date",
            "membership_registered_full_name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _prune_step_fields(self)


class MemberApplicationApprovalForm(forms.Form):
    membership_no = forms.CharField(
        max_length=50,
        label=_("Membership number"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Membership number"),
            }
        ),
    )

    def __init__(self, *args, tenant=None, application=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        self.application = application
        if not self.is_bound and application and application.has_membership_number:
            claimed_membership_no = (application.membership_number or "").strip()
            if claimed_membership_no:
                self.fields["membership_no"].initial = claimed_membership_no

    def clean_membership_no(self):
        membership_no = self.cleaned_data.get("membership_no", "").strip()
        if not membership_no:
            raise forms.ValidationError(_("Membership number is required."))
        
        if self.tenant:
            existing_by_number = Member.objects.filter(
                tenant=self.tenant,
                membership_no=membership_no,
            ).first()
            existing_for_user = None
            if self.application:
                existing_for_user = Member.objects.filter(
                    tenant=self.tenant,
                    username=self.application.user.username,
                ).first()

            if self.application and self.application.has_membership_number:
                if (
                    existing_by_number
                    and existing_for_user
                    and existing_by_number.pk != existing_for_user.pk
                ):
                    raise forms.ValidationError(
                        _(
                            "This claimed membership number belongs to a different member record while this user is already linked elsewhere. Resolve that conflict first."
                        )
                    )
                return membership_no

            if existing_by_number and (
                not existing_for_user or existing_by_number.pk != existing_for_user.pk
            ):
                raise forms.ValidationError(
                    _("A member with this membership number already exists. Please enter a different number.")
                )
        
        return membership_no


class SpiritualProgressForm(forms.ModelForm):
    baptism_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
    )
    confirmation_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
    )
    education_level = forms.ChoiceField(
        choices=[("", _("---------"))] + EDUCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = SpiritualProgress
        exclude = ["tenant", "member"]
        widgets = {
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "occupation": forms.TextInput(attrs={"class": "form-control"}),
            "work_place": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.label, str) and field.label:
                field.label = _(field.label)
            if isinstance(field.help_text, str) and field.help_text:
                field.help_text = _(field.help_text)
            placeholder = field.widget.attrs.get("placeholder")
            if isinstance(placeholder, str) and placeholder:
                field.widget.attrs["placeholder"] = _(placeholder)
