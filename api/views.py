import datetime

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from content_app.models import Announcement, DailyLiturgy
from fellowships.models import FellowshipGroup, FellowshipParticipation
from members.models import Member, SpiritualProgress
from pledges.models import Pledge
from tenants.models import Tenant

from .serializers import (
	AnnouncementSerializer,
	DailyLiturgySerializer,
	FellowshipGroupSerializer,
	FellowshipParticipationSerializer,
	MemberSerializer,
	PledgeSerializer,
	SpiritualProgressSerializer,
	TenantSerializer,
)


class TenantQuerysetMixin:
	def get_tenant(self):
		return getattr(self.request, "tenant", None)

	def get_queryset(self):
		qs = super().get_queryset()
		tenant = self.get_tenant()
		if tenant is None:
			return qs.none()
		return qs.filter(tenant=tenant)

	def perform_create(self, serializer):
		tenant = self.get_tenant()
		if tenant is None:
			raise ValidationError("Tenant could not be resolved.")
		serializer.save(tenant=tenant)


class TenantViewSet(viewsets.ModelViewSet):
	queryset = Tenant.objects.all()
	serializer_class = TenantSerializer
	permission_classes = [IsAdminUser]


class MemberViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
	queryset = Member.objects.all().prefetch_related("spiritual_progress")
	serializer_class = MemberSerializer
	filterset_fields = ["gender", "marital_status", "residence_name"]
	search_fields = ["full_name", "membership_no", "primary_phone"]


class SpiritualProgressViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
	queryset = SpiritualProgress.objects.select_related("member")
	serializer_class = SpiritualProgressSerializer
	filterset_fields = ["is_baptized", "is_confirmed", "takes_communion"]
	search_fields = ["member__full_name", "profession", "occupation"]


class FellowshipGroupViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
	queryset = FellowshipGroup.objects.all()
	serializer_class = FellowshipGroupSerializer
	search_fields = ["name", "leader_name"]


class FellowshipParticipationViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
	queryset = FellowshipParticipation.objects.select_related("member", "group")
	serializer_class = FellowshipParticipationSerializer
	filterset_fields = ["is_leader"]
	search_fields = ["member__full_name", "group__name"]


class PledgeViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
	queryset = Pledge.objects.select_related("member")
	serializer_class = PledgeSerializer
	filterset_fields = ["year"]
	search_fields = ["member__full_name", "member__membership_no"]


class AnnouncementViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
	queryset = Announcement.objects.all()
	serializer_class = AnnouncementSerializer
	filterset_fields = ["category", "is_active"]
	search_fields = ["title", "content"]


class DailyLiturgyViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
	queryset = DailyLiturgy.objects.all()
	serializer_class = DailyLiturgySerializer
	filterset_fields = ["date"]


class TodayLiturgyView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		tenant = getattr(request, "tenant", None)
		if tenant is None:
			return Response([], status=status.HTTP_200_OK)

		today = datetime.date.today()
		liturgy = DailyLiturgy.objects.filter(tenant=tenant, date=today).first()
		if liturgy is None:
			return Response({"detail": "No liturgy for today."}, status=status.HTTP_404_NOT_FOUND)

		serializer = DailyLiturgySerializer(liturgy)
		return Response(serializer.data, status=status.HTTP_200_OK)


class SkillSearchView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		tenant = getattr(request, "tenant", None)
		if tenant is None:
			return Response([], status=status.HTTP_200_OK)

		term = (
			request.query_params.get("profession")
			or request.query_params.get("q")
			or ""
		)
		qs = SpiritualProgress.objects.filter(tenant=tenant)
		if term:
			qs = qs.filter(Q(profession__icontains=term) | Q(occupation__icontains=term))

		serializer = SpiritualProgressSerializer(qs, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class BriqSmsWebhookView(APIView):
	"""Webhook endpoint for Briq SMS delivery/status callbacks.

	Verifies HMAC signature when BRIQ_WEBHOOK_SECRET is configured.
	"""

	authentication_classes = []
	permission_classes = [AllowAny]

	def post(self, request):
		from django.conf import settings

		from .briq import verify_briq_signature

		raw = request.body or b""
		secret = getattr(settings, "BRIQ_WEBHOOK_SECRET", "") or ""

		signature = (
			request.headers.get("X-Briq-Signature")
			or request.headers.get("X-Signature")
			or request.headers.get("X-Hub-Signature-256")
			or ""
		)

		if secret:
			if not verify_briq_signature(
				raw_body=raw,
				secret=secret,
				signature_header=signature,
			):
				return Response({"detail": "Invalid signature"}, status=401)

		# We accept the payload (structure depends on Briq configuration)
		return Response({"ok": True}, status=200)
