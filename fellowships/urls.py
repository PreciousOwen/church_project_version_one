from django.urls import path

from . import views

app_name = "fellowships"

urlpatterns = [
    path("", views.FellowshipGroupListView.as_view(), name="list"),
    path("add/", views.FellowshipGroupCreateView.as_view(), name="create"),
    path("<int:pk>/", views.FellowshipGroupDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.FellowshipGroupUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.FellowshipGroupDeleteView.as_view(), name="delete"),
    path("participation/add/", views.ParticipationCreateView.as_view(), name="participation-add"),
]
