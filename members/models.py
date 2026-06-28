from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from tenants.models import TenantAwareModel


class Member(TenantAwareModel):
	membership_no = models.CharField(max_length=50)
	username = models.CharField(max_length=80, blank=True)
	password = models.CharField(max_length=128, blank=True)
	full_name = models.CharField(max_length=200)
	gender = models.CharField(max_length=10)
	dob = models.DateField()
	place_of_birth = models.CharField(max_length=200, blank=True)
	marital_status = models.CharField(max_length=20)
	marriage_type = models.CharField(max_length=50, blank=True)
	marriage_date = models.DateField(null=True, blank=True)
	marriage_place = models.CharField(max_length=200, blank=True)
	spouse_name = models.CharField(max_length=200, blank=True)
	living_with_spouse_name = models.CharField(max_length=200, blank=True)
	dependents = models.JSONField(default=list, blank=True, null=True)

	primary_phone = models.CharField(max_length=20)
	spouse_phone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	po_box = models.CharField(max_length=50, blank=True)
	house_number = models.CharField(max_length=50, blank=True)
	residence_name = models.CharField(max_length=100, blank=True)
	block_number = models.CharField(max_length=50, blank=True)
	fellowship_name = models.CharField(max_length=100, blank=True)

	previous_parish = models.CharField(max_length=200, blank=True)
	neighbor_name = models.CharField(max_length=200, blank=True)
	neighbor_phone = models.CharField(max_length=20, blank=True)
	elder_name = models.CharField(max_length=200, blank=True)
	elder_phone = models.CharField(max_length=20, blank=True)
	occupation = models.CharField(max_length=100, blank=True)
	work_place = models.CharField(max_length=200, blank=True)
	education_level = models.CharField(max_length=50, blank=True)
	profession = models.CharField(max_length=100, blank=True)
	volunteer_status = models.BooleanField(default=False)

	is_baptized = models.BooleanField(default=False)
	baptism_date = models.DateField(null=True, blank=True)
	is_confirmed = models.BooleanField(default=False)
	confirmation_date = models.DateField(null=True, blank=True)
	participates_in_sacraments = models.BooleanField(default=False)

	participates_in_fellowship = models.BooleanField(default=False)
	fellowship_house_name = models.CharField(max_length=200, blank=True)
	fellowship_non_participation_reason = models.TextField(blank=True)
	fellowship_chairperson_name = models.CharField(max_length=200, blank=True)
	fellowship_chairperson_signature = models.CharField(max_length=200, blank=True)

	join_fellowship = models.BooleanField(default=False)
	join_sunday_school = models.BooleanField(default=False)
	join_visiting_sick = models.BooleanField(default=False)
	join_bible_study = models.BooleanField(default=False)
	join_choir = models.BooleanField(default=False)
	join_union = models.BooleanField(default=False)
	pledge_year = models.IntegerField(default=0)
	pledge_building = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	pledge_stewardship = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	pledge_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	has_membership_number = models.BooleanField(default=False)
	membership_registration_date = models.DateField(null=True, blank=True)
	membership_registered_full_name = models.CharField(max_length=200, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["full_name"]
		constraints = [
			models.UniqueConstraint(
				fields=["tenant", "membership_no"],
				name="uniq_member_membership_per_tenant",
			),
			models.UniqueConstraint(
				fields=["tenant", "username"],
				name="uniq_member_username_per_tenant",
			),
		]

	def save(self, *args, **kwargs):
		if self.membership_no:
			normalized = "".join(self.membership_no.split()).upper()
			self.membership_no = normalized
			if not self.username:
				self.username = f"KKKT{normalized}"
		if self.password:
			try:
				identify_hasher(self.password)
			except ValueError:
				self.password = make_password(self.password)
		super().save(*args, **kwargs)

	def __str__(self) -> str:
		return f"{self.full_name} ({self.membership_no})"


class SpiritualProgress(TenantAwareModel):
	member = models.OneToOneField(
		Member,
		on_delete=models.CASCADE,
		related_name="spiritual_progress",
	)
	is_baptized = models.BooleanField(default=False)
	baptism_date = models.DateField(null=True, blank=True)
	is_confirmed = models.BooleanField(default=False)
	confirmation_date = models.DateField(null=True, blank=True)
	takes_communion = models.BooleanField(default=False)

	profession = models.CharField(max_length=100, blank=True)
	education_level = models.CharField(max_length=50, blank=True)
	occupation = models.CharField(max_length=100, blank=True)
	work_place = models.CharField(max_length=200, blank=True)
	volunteer_status = models.BooleanField(default=False)

	class Meta:
		ordering = ["member__full_name"]

	def __str__(self) -> str:
		return f"Progress for {self.member.full_name}"


class MemberApplication(TenantAwareModel):
	STATUS_PENDING = "pending"
	STATUS_APPROVED = "approved"
	STATUS_REJECTED = "rejected"

	STATUS_CHOICES = [
		(STATUS_PENDING, _("Pending")),
		(STATUS_APPROVED, _("Approved")),
		(STATUS_REJECTED, _("Rejected")),
	]

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="member_application",
	)
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default=STATUS_PENDING,
	)
	assigned_membership_no = models.CharField(max_length=50, blank=True)
	reviewed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="reviewed_member_applications",
	)
	reviewed_at = models.DateTimeField(null=True, blank=True)

	full_name = models.CharField(max_length=200)
	gender = models.CharField(max_length=10)
	dob = models.DateField()
	place_of_birth = models.CharField(max_length=200, blank=True)
	marital_status = models.CharField(max_length=20)
	marriage_type = models.CharField(max_length=50, blank=True)
	marriage_date = models.DateField(null=True, blank=True)
	marriage_place = models.CharField(max_length=200, blank=True)
	spouse_name = models.CharField(max_length=200, blank=True)
	living_with_spouse_name = models.CharField(max_length=200, blank=True)
	dependents = models.JSONField(default=list, blank=True, null=True)

	primary_phone = models.CharField(max_length=20)
	spouse_phone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	po_box = models.CharField(max_length=50, blank=True)
	house_number = models.CharField(max_length=50, blank=True)
	residence_name = models.CharField(max_length=100, blank=True)
	block_number = models.CharField(max_length=50, blank=True)
	fellowship_name = models.CharField(max_length=100, blank=True)

	previous_parish = models.CharField(max_length=200, blank=True)
	neighbor_name = models.CharField(max_length=200, blank=True)
	neighbor_phone = models.CharField(max_length=20, blank=True)
	elder_name = models.CharField(max_length=200, blank=True)
	elder_phone = models.CharField(max_length=20, blank=True)
	occupation = models.CharField(max_length=100, blank=True)
	work_place = models.CharField(max_length=200, blank=True)
	education_level = models.CharField(max_length=50, blank=True)
	profession = models.CharField(max_length=100, blank=True)
	volunteer_status = models.BooleanField(default=False)

	is_baptized = models.BooleanField(default=False)
	baptism_date = models.DateField(null=True, blank=True)
	is_confirmed = models.BooleanField(default=False)
	confirmation_date = models.DateField(null=True, blank=True)
	participates_in_sacraments = models.BooleanField(default=False)

	participates_in_fellowship = models.BooleanField(default=False)
	fellowship_house_name = models.CharField(max_length=200, blank=True)
	fellowship_non_participation_reason = models.TextField(blank=True)
	fellowship_chairperson_name = models.CharField(max_length=200, blank=True)
	fellowship_chairperson_signature = models.CharField(max_length=200, blank=True)

	join_fellowship = models.BooleanField(default=False)
	join_sunday_school = models.BooleanField(default=False)
	join_visiting_sick = models.BooleanField(default=False)
	join_bible_study = models.BooleanField(default=False)
	join_choir = models.BooleanField(default=False)
	join_union = models.BooleanField(default=False)
	pledge_year = models.IntegerField(default=0)
	pledge_building = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	pledge_stewardship = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	pledge_other = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	has_membership_number = models.BooleanField(default=False)
	membership_number = models.CharField(max_length=50, blank=True)
	membership_registration_date = models.DateField(null=True, blank=True)
	membership_registered_full_name = models.CharField(max_length=200, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"Application: {self.full_name} ({self.get_status_display()})"
