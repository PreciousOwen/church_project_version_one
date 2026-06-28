from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Tenant


def _normalize_phone_if_applicable(value: str) -> str:
    from .briq_otp import normalize_tz_phone

    raw = (value or "").strip()
    if any(ch.isalpha() for ch in raw):
        return raw
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) == 9 or (len(digits) == 10 and digits.startswith("0")):
        return normalize_tz_phone(digits)
    if len(digits) == 12 and digits.startswith("255"):
        return normalize_tz_phone(digits)
    return raw


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ["name", "slug", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PhoneLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Phone number or admin username"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "621437851 or admin",
                "autocomplete": "username",
            }
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].error_messages["required"] = _(
            "Enter your phone number or admin username."
        )
        self.fields["password"].error_messages["required"] = _("Enter your password.")
        self.fields["password"].widget.attrs.update({"class": "form-control"})

    def clean_username(self):
        value = (self.cleaned_data.get("username", "") or "").strip()
        normalized = _normalize_phone_if_applicable(value)
        if not normalized:
            raise forms.ValidationError(_("Enter a valid phone number."))
        return normalized

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if not username or not password:
            return self.cleaned_data

        User = get_user_model()
        existing_user = User._default_manager.filter(username=username).first()
        is_phone_login = username.isdigit() and username.startswith("255") and len(username) == 12
        if not existing_user:
            if is_phone_login:
                raise forms.ValidationError(_("No account found with this phone number."))
            raise forms.ValidationError(_("No account found with this username."))
        if not existing_user.check_password(password):
            if is_phone_login:
                raise forms.ValidationError(_("Incorrect password for this phone number."))
            raise forms.ValidationError(_("Incorrect password for this username."))

        self.user_cache = authenticate(self.request, username=username, password=password)
        if self.user_cache is None:
            raise forms.ValidationError(_("Unable to sign in with these credentials."))
        self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("Your account is not active yet. Please verify your phone number.")
            )


class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(
        label=_("Phone number"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "placeholder": "621437851",
                "maxlength": "12",
                "autocomplete": "tel",
            }
        ),
    )

    def clean_username(self):
        normalized = _normalize_phone_if_applicable(self.cleaned_data.get("username", ""))
        if not normalized or not (normalized.isdigit() and normalized.startswith("255") and len(normalized) == 12):
            raise forms.ValidationError(_("Enter a valid phone number."))

        User = get_user_model()
        user = User.objects.filter(username=normalized).first()
        if not user:
            raise forms.ValidationError(_("No account found with this phone number."))
        if not user.is_active:
            raise forms.ValidationError(_("This account is not active. Complete verification first."))
        return normalized


class PasswordResetSetForm(forms.Form):
    password1 = forms.CharField(
        label=_("New password (minimum 6 digits)"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label=_("Confirm new password (minimum 6 digits)"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    def clean_password1(self):
        password = self.cleaned_data.get("password1", "")
        if len(password) < 6:
            raise forms.ValidationError(_("Password must be at least 6 digits long."))
        if not password.isdigit():
            raise forms.ValidationError(_("Password must contain digits only."))
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("Passwords do not match."))
        return cleaned


class PhoneSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "numeric",
                    "placeholder": "621437851",
                    "maxlength": "10",
                    "autocomplete": "tel",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Phone number")
        self.fields["username"].help_text = ""
        self.fields["password1"].label = _("Password (minimum 6 digits)")
        self.fields["password1"].help_text = ""
        self.fields["password2"].label = _("Confirm password (minimum 6 digits)")
        self.fields["password2"].help_text = ""
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs.update({"class": "form-control"})

    def clean_username(self):
        from .briq_otp import normalize_tz_phone
        from django.contrib.auth import get_user_model

        phone = (self.cleaned_data.get("username", "") or "").strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) == 9:
            normalized = normalize_tz_phone(digits)
        elif len(digits) == 10 and digits.startswith("0"):
            normalized = normalize_tz_phone(digits)
        else:
            normalized = ""
        if not normalized:
            raise forms.ValidationError(_("Enter 9 digits (e.g. 621437851) or 10 digits starting with 0."))
        
        # Check if user with this phone number already exists
        User = get_user_model()
        if User.objects.filter(username=normalized).exists():
            raise forms.ValidationError(_("A user with this phone number already exists."))
        
        return normalized

    def clean_password1(self):
        password = self.cleaned_data.get("password1", "")
        if len(password) < 6:
            raise forms.ValidationError(_("Password must be at least 6 characters long."))
        return password

    def _post_clean(self):
        # Skip Django's global AUTH_PASSWORD_VALIDATORS for signup;
        # only our 6-character minimum rule applies.
        super(BaseUserCreationForm, self)._post_clean()


class OtpVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=10,
        label=_("Verification code"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "placeholder": "123456",
            }
        ),
    )
