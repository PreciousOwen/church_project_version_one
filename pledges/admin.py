from django.contrib import admin

from .models import Pledge


@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
	list_display = ("member", "year", "building_pledge", "stewardship_pledge")
	list_filter = ("year",)
	search_fields = ("member__full_name", "member__membership_no")
