from rest_framework.serializers import ModelSerializer

from referal.models import UserModel, InviteCodeUsageModel


class UserProfileSerializer(ModelSerializer):

    class Meta:
        model = UserModel
        fields = ["id", "phone_number", "username", "first_name"]

class InviteCodeUsageSerializer(ModelSerializer):
    class Meta:
        model = InviteCodeUsageModel
        fields = ["invite_code", "user", "used_at", "is_revoked"]