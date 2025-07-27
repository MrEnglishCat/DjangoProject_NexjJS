import re
import time
from datetime import datetime, UTC

from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response  # Не забудьте импортировать Response

from referal.models import AuthSessionModel, UserModel, InviteCodeModel, InviteCodeUsageModel
from referal.serializers import UserProfileSerializer, InviteCodeSerializer, InviteCodeUsageSerializer


class InviteCodeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Response должен возвращать словарь, а не просто строку
        return Response({"success": True, "message": "Запрос на формирование инвайт кода получен"})


class RequestCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
            Нужно получить номер,
            Сформировать 4х значиный код через таблицу сессий AuthSessionModel - имитация сессий
            Отправить пользователю этот код
        :param request:
        :return:
        """

        phone_number = ''.join(re.findall(r"\d+", request.data.get('phone_number', '')))
        print("phone_number", phone_number)
        if not phone_number:
            return Response({"success": False, "message": "Не передан номер телефона!"},
                            status=status.HTTP_400_BAD_REQUEST)

        auth_code_from_db = AuthSessionModel.objects.filter(phone_number=phone_number,
                                                            expires_at__gt=datetime.now(UTC), is_used=False).first()
        if auth_code_from_db:
            return Response({"success": True, "message": "Код для авторизации создан", "phone_number": phone_number,
                             "auth_code": auth_code_from_db.code}, status=status.HTTP_200_OK)

        auth_code: AuthSessionModel = AuthSessionModel.create_session(phone_number=phone_number)
        time.sleep(1.5)  # имитация обращения к API SMS

        return Response(
            {"success": True, "message": "Код для авторизации создан", "phone_number": phone_number,
             "auth_code": auth_code.code}, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = ''.join(re.findall(r"\d+", request.data.get('phone_number', '')))
        user_auth_code = request.data.get('auth_code')
        time.sleep(1.5)
        if not phone_number or not user_auth_code:
            return Response({"success": False, "message": "Не передан номер телефона или код авторизации!"},
                            status=status.HTTP_400_BAD_REQUEST)

        auth_code_from_db = AuthSessionModel.objects.filter(phone_number=phone_number,
                                                            expires_at__gt=datetime.now(UTC), is_used=False).first()

        if auth_code_from_db and user_auth_code == auth_code_from_db.code:
            auth_code_from_db.is_used = True
            invite_code = InviteCodeModel.generate_unique_code()
            user, create = UserModel.objects.get_or_create(phone_number=phone_number)
            if not (InviteCodeModel.objects.filter(user_id=user.id, is_active=True)):
                try:
                    _invite_code_obj, create = InviteCodeModel.objects.get_or_create(code=invite_code, user_id=user.id,
                                                                                     is_active=True)
                    InviteCodeUsageModel.objects.get_or_create(invite_code=_invite_code_obj, user_id=user.id)
                except IntegrityError:
                    _invite_code = InviteCodeModel.objects.get(user_id=user.id, )

            auth_code_from_db.save()

            return Response({
                "success": True,
                "message": f"Авторизация пройдена успешно {phone_number}. {auth_code_from_db.code}, {auth_code_from_db.expires_at}"},
                status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": "Cрок действия кода истек или код был использован. Отправьте запрос повторно для генерации кода."},
                status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, phone_number=None):
        if not phone_number or not phone_number.isdigit():
            return Response({"success": False, "message": "Номер телефона не передан или у номера неверный формат!"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserModel.objects.get(phone_number=phone_number)
            _invite_code_usage = (InviteCodeModel.objects.filter(is_active=True, user_id=user.id).first()).usages.all()
            print("_invite_code_usage", _invite_code_usage)
        except UserModel.DoesNotExist:
            return Response({"success": False, "message": "Пользователь не найден!"}, status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                "success": True,
                "user": UserProfileSerializer(user).data,
                "invite_codes_usage": InviteCodeUsageSerializer(_invite_code_usage, many=True).data
            },
            status=status.HTTP_200_OK
        )
