from django.db import models


class Tenant(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:
		return self.name


class TenantAwareModel(models.Model):
	tenant = models.ForeignKey(
		Tenant,
		on_delete=models.PROTECT,
		related_name="%(class)s_records",
	)

	class Meta:
		abstract = True
