from django.urls import path

from . import views

app_name = "pledges"

urlpatterns = [
    path("", views.PledgeListView.as_view(), name="list"),
    path("add/", views.PledgeCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.PledgeUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.PledgeDeleteView.as_view(), name="delete"),
]
