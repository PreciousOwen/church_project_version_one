from decimal import Decimal, InvalidOperation

from django import forms

from .models import Pledge


class PledgeForm(forms.ModelForm):
    year = forms.CharField(
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
    building_pledge = forms.CharField(
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
    stewardship_pledge = forms.CharField(
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
    other_pledges = forms.CharField(
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

    class Meta:
        model = Pledge
        exclude = ["tenant", "submission_date"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
        }

    def _parse_decimal(self, value, field_name):
        if value in (None, ""):
            return Decimal("0")
        try:
            return Decimal(str(value).replace(",", ""))
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Enter a valid number.")

    def clean_year(self):
        value = self.cleaned_data.get("year")
        if value in (None, ""):
            return 0
        try:
            return int(str(value).replace(",", ""))
        except (TypeError, ValueError):
            raise forms.ValidationError("Enter a valid year.")

    def clean_building_pledge(self):
        return self._parse_decimal(self.cleaned_data.get("building_pledge"), "building_pledge")

    def clean_stewardship_pledge(self):
        return self._parse_decimal(self.cleaned_data.get("stewardship_pledge"), "stewardship_pledge")

    def clean_other_pledges(self):
        return self._parse_decimal(self.cleaned_data.get("other_pledges"), "other_pledges")
