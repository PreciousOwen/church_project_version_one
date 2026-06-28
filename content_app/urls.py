from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("announcements/", views.AnnouncementListView.as_view(), name="announcements"),
    path("announcements/add/", views.AnnouncementCreateView.as_view(), name="announcement-add"),
    path("announcements/<int:pk>/edit/", views.AnnouncementUpdateView.as_view(), name="announcement-update"),
    path("announcements/<int:pk>/delete/", views.AnnouncementDeleteView.as_view(), name="announcement-delete"),
    path("upcoming-events/", views.UpcomingEventListView.as_view(), name="upcoming-events"),
    path("upcoming-events/add/", views.UpcomingEventCreateView.as_view(), name="upcoming-event-add"),
    path("upcoming-events/<int:pk>/edit/", views.UpcomingEventUpdateView.as_view(), name="upcoming-event-update"),
    path("upcoming-events/<int:pk>/delete/", views.UpcomingEventDeleteView.as_view(), name="upcoming-event-delete"),
    path("liturgy/", views.DailyLiturgyListView.as_view(), name="liturgy"),
    path("liturgy/add/", views.DailyLiturgyCreateView.as_view(), name="liturgy-add"),
    path("liturgy/<int:pk>/edit/", views.DailyLiturgyUpdateView.as_view(), name="liturgy-update"),
]
