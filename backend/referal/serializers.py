from rest_framework.serializers import ModelSerializer

from referal.models import UserModel


class UserProfileSerializer(ModelSerializer):

    class Meta:
        model = UserModel
        fields = ["phone_number", "username", "first_name"]