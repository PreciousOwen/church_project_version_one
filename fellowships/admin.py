from django.contrib import admin

from .models import FellowshipGroup, FellowshipParticipation


@admin.register(FellowshipGroup)
class FellowshipGroupAdmin(admin.ModelAdmin):
	list_display = ("name", "leader_name", "leader_phone")
	search_fields = ("name", "leader_name")


@admin.register(FellowshipParticipation)
class FellowshipParticipationAdmin(admin.ModelAdmin):
	list_display = ("member", "group", "is_leader", "joined_date")
	list_filter = ("is_leader",)
	search_fields = ("member__full_name", "group__name")
