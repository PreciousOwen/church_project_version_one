from django import forms

from .models import Announcement, DailyLiturgy, UpcomingEvent


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        exclude = ["tenant", "published_at"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }


class DailyLiturgyForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    class Meta:
        model = DailyLiturgy
        exclude = ["tenant"]
        widgets = {
            "readings": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "order_of_service": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "hymns": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "verse_of_the_day": forms.TextInput(attrs={"class": "form-control"}),
        }


class UpcomingEventForm(forms.ModelForm):
    event_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = UpcomingEvent
        exclude = ["tenant", "created_at"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
