from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnnouncementViewSet,
    DailyLiturgyViewSet,
    FellowshipGroupViewSet,
    FellowshipParticipationViewSet,
    MemberViewSet,
    PledgeViewSet,
    SkillSearchView,
    SpiritualProgressViewSet,
    TenantViewSet,
    TodayLiturgyView,
)

router = DefaultRouter()
router.register("tenants", TenantViewSet, basename="tenant")
router.register("members", MemberViewSet, basename="member")
router.register("spiritual-progress", SpiritualProgressViewSet, basename="spiritual-progress")
router.register("fellowships", FellowshipGroupViewSet, basename="fellowship")
router.register("fellowship-participation", FellowshipParticipationViewSet, basename="fellowship-participation")
router.register("pledges", PledgeViewSet, basename="pledge")
router.register("announcements", AnnouncementViewSet, basename="announcement")
router.register("liturgy", DailyLiturgyViewSet, basename="liturgy")

urlpatterns = [
    path("liturgy/today/", TodayLiturgyView.as_view(), name="liturgy-today"),
    path("skill-search/", SkillSearchView.as_view(), name="skill-search"),
    path("", include(router.urls)),
]
