from rest_framework import serializers

from content_app.models import Announcement, DailyLiturgy
from fellowships.models import FellowshipGroup, FellowshipParticipation
from members.models import Member, SpiritualProgress
from pledges.models import Pledge
from tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "slug", "is_active"]


class MemberSerializer(serializers.ModelSerializer):
    spiritual_progress = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id",
            "membership_no",
            "full_name",
            "gender",
            "dob",
            "place_of_birth",
            "marital_status",
            "marriage_type",
            "marriage_date",
            "marriage_place",
            "spouse_name",
            "living_with_spouse_name",
            "dependents",
            "primary_phone",
            "spouse_phone",
            "email",
            "po_box",
            "house_number",
            "residence_name",
            "block_number",
            "previous_parish",
            "fellowship_name",
            "neighbor_name",
            "neighbor_phone",
            "elder_name",
            "elder_phone",
            "occupation",
            "work_place",
            "education_level",
            "profession",
            "volunteer_status",
            "is_baptized",
            "baptism_date",
            "is_confirmed",
            "confirmation_date",
            "participates_in_sacraments",
            "participates_in_fellowship",
            "fellowship_house_name",
            "fellowship_non_participation_reason",
            "fellowship_chairperson_name",
            "fellowship_chairperson_signature",
            "join_fellowship",
            "join_sunday_school",
            "join_visiting_sick",
            "join_bible_study",
            "join_choir",
            "join_union",
            "created_at",
            "updated_at",
            "spiritual_progress",
        ]

    def get_spiritual_progress(self, obj):
        progress = getattr(obj, "spiritual_progress", None)
        if not progress:
            return None
        return SpiritualProgressSerializer(progress, context=self.context).data


class SpiritualProgressSerializer(serializers.ModelSerializer):
    member_detail = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "tenant") and request.tenant:
            self.fields["member"].queryset = Member.objects.filter(tenant=request.tenant)

    def get_member_detail(self, obj):
        return MemberSerializer(obj.member, context=self.context).data

    class Meta:
        model = SpiritualProgress
        fields = [
            "id",
            "member",
            "member_detail",
            "is_baptized",
            "baptism_date",
            "is_confirmed",
            "confirmation_date",
            "takes_communion",
            "profession",
            "education_level",
            "occupation",
            "work_place",
            "volunteer_status",
        ]


class FellowshipGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FellowshipGroup
        fields = ["id", "name", "description", "leader_name", "leader_phone"]


class FellowshipParticipationSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "tenant") and request.tenant:
            tenant = request.tenant
            self.fields["member"].queryset = Member.objects.filter(tenant=tenant)
            self.fields["group_id"].queryset = FellowshipGroup.objects.filter(tenant=tenant)
    group = FellowshipGroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=FellowshipGroup.objects.all(),
        source="group",
        write_only=True,
    )

    class Meta:
        model = FellowshipParticipation
        fields = ["id", "member", "group", "group_id", "is_leader", "joined_date"]


class PledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pledge
        fields = [
            "id",
            "member",
            "year",
            "building_pledge",
            "stewardship_pledge",
            "other_pledges",
            "submission_date",
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ["id", "title", "content", "category", "published_at", "is_active"]


class DailyLiturgySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLiturgy
        fields = [
            "id",
            "date",
            "readings",
            "order_of_service",
            "hymns",
            "verse_of_the_day",
        ]
