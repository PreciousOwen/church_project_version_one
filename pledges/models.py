from django.db import models

from members.models import Member
from tenants.models import TenantAwareModel


class Pledge(TenantAwareModel):
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
	year = models.IntegerField(default=2026)
	building_pledge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	stewardship_pledge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	other_pledges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	submission_date = models.DateField(auto_now_add=True)

	class Meta:
		ordering = ["-year", "member__full_name"]
		constraints = [
			models.UniqueConstraint(
				fields=["tenant", "member", "year"],
				name="uniq_member_year_pledge_per_tenant",
			)
		]

	def __str__(self) -> str:
		return f"{self.member.full_name} {self.year}"
