from django.contrib import admin

from .models import Announcement, DailyLiturgy, UpcomingEvent


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "published_at", "is_active")
	list_filter = ("category", "is_active")
	search_fields = ("title", "content")


@admin.register(DailyLiturgy)
class DailyLiturgyAdmin(admin.ModelAdmin):
	list_display = ("date", "verse_of_the_day")
	search_fields = ("verse_of_the_day",)


@admin.register(UpcomingEvent)
class UpcomingEventAdmin(admin.ModelAdmin):
	list_display = ("title", "event_date", "is_active", "created_at")
	list_filter = ("is_active",)
	search_fields = ("title", "description")
