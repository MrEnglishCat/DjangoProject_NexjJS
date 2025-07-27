from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from referal.models import UserModel, InviteCodeUsageModel, InviteCodeModel


class UserProfileSerializer(ModelSerializer):
    invite_code = SerializerMethodField()
    invite_codes = SerializerMethodField()


    def get_invite_code(self, obj):
        print("obj", obj)
        invite_code_obj = InviteCodeModel.objects.select_related('user').filter(user=obj, is_active=True).first()
        return InviteCodeSerializer(invite_code_obj).data

    def get_invite_codes(self, obj):
        invite_code_obj = InviteCodeModel.objects.select_related('user').filter(user=obj)
        return InviteCodeSerializer(invite_code_obj, many=True).data

    class Meta:
        model = UserModel
        fields = ["id", "phone_number", "username", "first_name", "invite_code", "invite_codes"]


class InviteCodeSerializer(ModelSerializer):

    class Meta:
        model = InviteCodeModel
        fields = ["invite_code", "is_active", "user", "created_at", "updated_at"]


class InviteCodeUsageSerializer(ModelSerializer):
    user_phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    invite_code = serializers.CharField(source='invite_code.code', read_only=True)
    class Meta:
        model = InviteCodeUsageModel
        fields = ["invite_code", "user_phone_number", "used_at", "is_revoked"]