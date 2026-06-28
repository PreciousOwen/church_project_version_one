from django import forms

from .models import FellowshipGroup, FellowshipParticipation


class FellowshipGroupForm(forms.ModelForm):
    class Meta:
        model = FellowshipGroup
        exclude = ["tenant"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "leader_name": forms.TextInput(attrs={"class": "form-control"}),
            "leader_phone": forms.TextInput(attrs={"class": "form-control"}),
        }


class FellowshipParticipationForm(forms.ModelForm):
    class Meta:
        model = FellowshipParticipation
        exclude = ["tenant"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-select"}),
            "group": forms.Select(attrs={"class": "form-select"}),
        }
