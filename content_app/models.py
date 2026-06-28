from django.db import models

from tenants.models import TenantAwareModel


class Announcement(TenantAwareModel):
	CATEGORY_CHOICES = [
		("wedding", "Wedding Bans"),
		("funeral", "Funerals"),
		("general", "General"),
	]

	title = models.CharField(max_length=200)
	content = models.TextField()
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
	published_at = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["-published_at"]

	def __str__(self) -> str:
		return self.title


class DailyLiturgy(TenantAwareModel):
	date = models.DateField()
	readings = models.TextField()
	order_of_service = models.TextField()
	hymns = models.TextField()
	verse_of_the_day = models.CharField(max_length=300)

	class Meta:
		ordering = ["-date"]
		constraints = [
			models.UniqueConstraint(
				fields=["tenant", "date"],
				name="uniq_liturgy_date_per_tenant",
			)
		]

	def __str__(self) -> str:
		return str(self.date)


class UpcomingEvent(TenantAwareModel):
	title = models.CharField(max_length=200)
	description = models.TextField()
	image = models.ImageField(upload_to="upcoming_events/")
	event_date = models.DateField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["event_date", "-created_at"]

	def __str__(self) -> str:
		return self.title
