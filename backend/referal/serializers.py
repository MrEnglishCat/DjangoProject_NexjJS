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
        fields = ["id", "phone_number", "username", "first_name", "last_name", "email", "invite_code", "invite_codes"]

class UserProfileEditSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "phone_number", "username", "first_name", "last_name", "email"]


class InviteCodeSerializer(ModelSerializer):

    created_at = serializers.DateTimeField(read_only=True, format="%d.%m.%Y %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%d.%m.%Y %H:%M:%S")

    class Meta:
        model = InviteCodeModel
        fields = ["invite_code", "is_active", "user", "created_at", "updated_at"]

class ActivateInviteCodeSerializer(serializers.Serializer):

    invite_code = serializers.CharField(max_length=6, min_length=6, required=True)
    user_id = serializers.IntegerField()

    def validate_invite_code(self, value):
        try:
            _invite_code_obj = InviteCodeModel.objects.get(invite_code=value)
            print("serializer", _invite_code_obj)
            return value
        except InviteCodeModel.DoesNotExist:
            raise serializers.ValidationError("Неверный инвайт код! Его не существует!")

    def validate_user_id(self, value):
        try:
            _user_obj = UserModel.objects.get(id=value)
            print("serializer", _user_obj)
            return value
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден!")

    def validate(self, attrs):
        print("attrs", attrs)
        invite_code = attrs["invite_code"]
        user_id = attrs["user_id"]
        if invite_code is None:
            raise serializers.ValidationError({"invite_code": "Это поле обязательно для заполнения."})
        if user_id is None:
            raise serializers.ValidationError({"user_id": "Это поле обязательно для заполнения."})

        try:
            _invite_code_obj = InviteCodeModel.objects.get(invite_code=invite_code)
            if _invite_code_obj.user and _invite_code_obj.user.id == user_id:
                raise serializers.ValidationError("Нельзя повторно активировать свой собственный код!")
            elif _invite_code_obj.user and _invite_code_obj.user.id != user_id:
                user_instance = UserModel.objects.get(id=user_id)
                invite_obj, create = InviteCodeUsageModel.objects.get_or_create(
                    invite_code=_invite_code_obj,
                    user=user_instance,
                )

                invite_obj.is_revoked = True
                invite_obj.save()

                # raise serializers.ValidationError("Попытка активации чужого инвайт-кода! Данные сохранены!")
        except InviteCodeModel.DoesNotExist:
            ...

        return attrs


class InviteCodeUsageSerializer(ModelSerializer):
    user_phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    invite_code = serializers.CharField(source='invite_code.code', read_only=True)
    class Meta:
        model = InviteCodeUsageModel
        fields = ["invite_code", "user_phone_number", "used_at", "is_revoked"]