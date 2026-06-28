from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("", views.MemberListView.as_view(), name="list"),
    path("add/", views.MemberWizardStepView.as_view(), {"step": 1}, name="create"),
    path("add/step/<int:step>/", views.MemberWizardStepView.as_view(), name="create-step"),
    path("apply/", views.MemberApplicationWizardStepView.as_view(), {"step": 1}, name="apply"),
    path("apply/step/<int:step>/", views.MemberApplicationWizardStepView.as_view(), name="apply-step"),
    path("apply/submitted/", views.MemberApplicationSubmittedView.as_view(), name="apply-submitted"),
    path("applications/", views.MemberApplicationListView.as_view(), name="applications"),
    path("applications/<int:pk>/", views.MemberApplicationApproveView.as_view(), name="application-approve"),
    path("me/", views.MemberProfileView.as_view(), name="me"),
    path("<int:pk>/", views.MemberDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.MemberUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.MemberDeleteView.as_view(), name="delete"),
    path(
        "<int:member_pk>/spiritual-progress/",
        views.SpiritualProgressView.as_view(),
        name="spiritual-progress",
    ),
]
