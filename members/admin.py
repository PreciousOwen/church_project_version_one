from django.contrib import admin

from .models import Member, MemberApplication, SpiritualProgress


class SpiritualProgressInline(admin.StackedInline):
	model = SpiritualProgress
	extra = 0


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
	list_display = (
		"full_name",
		"membership_no",
		"username",
		"primary_phone",
		"residence_name",
	)
	search_fields = ("full_name", "membership_no", "username", "primary_phone")
	list_filter = ("gender", "marital_status")
	inlines = [SpiritualProgressInline]


@admin.register(SpiritualProgress)
class SpiritualProgressAdmin(admin.ModelAdmin):
	list_display = ("member", "is_baptized", "is_confirmed", "takes_communion")
	search_fields = ("member__full_name",)


@admin.register(MemberApplication)
class MemberApplicationAdmin(admin.ModelAdmin):
	list_display = ("full_name", "primary_phone", "status", "created_at")
	search_fields = ("full_name", "primary_phone", "email")
	list_filter = ("status",)
