from django.db import models

from members.models import Member
from tenants.models import TenantAwareModel


class FellowshipGroup(TenantAwareModel):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	leader_name = models.CharField(max_length=200)
	leader_phone = models.CharField(max_length=20)

	class Meta:
		ordering = ["name"]
		constraints = [
			models.UniqueConstraint(
				fields=["tenant", "name"],
				name="uniq_fellowship_name_per_tenant",
			)
		]

	def __str__(self) -> str:
		return self.name


class FellowshipParticipation(TenantAwareModel):
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
	group = models.ForeignKey(FellowshipGroup, on_delete=models.CASCADE)
	is_leader = models.BooleanField(default=False)
	joined_date = models.DateField(auto_now_add=True)

	class Meta:
		ordering = ["group__name", "member__full_name"]
		constraints = [
			models.UniqueConstraint(
				fields=["tenant", "member", "group"],
				name="uniq_member_group_per_tenant",
			)
		]

	def __str__(self) -> str:
		return f"{self.member.full_name} in {self.group.name}"
