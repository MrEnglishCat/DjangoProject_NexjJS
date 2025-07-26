import re
import time
from datetime import datetime, UTC

from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response  # Не забудьте импортировать Response

from referal.models import AuthSessionModel, UserModel, InviteCodeModel
from referal.serializers import UserProfileSerializer

# Create your views here.

class InviteCodeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Response должен возвращать словарь, а не просто строку
        return Response({"message": "Запрос на формирование инвайт кода получен"})


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
            return Response({"message": "Не передан номер телефона!"}, status=status.HTTP_400_BAD_REQUEST)

        # Не точ

        auth_code_from_db = AuthSessionModel.objects.filter(phone_number=phone_number,
                                                            expires_at__gt=datetime.now(UTC), is_used=False).first()
        if auth_code_from_db:
            return Response({"message": "Код для авторизации создан", "phone_number": phone_number,
                             "auth_code": auth_code_from_db.code})

        auth_code: AuthSessionModel = AuthSessionModel.create_session(phone_number=phone_number)
        time.sleep(1.5)  # имитация обращения к API SMS

        return Response(
            {"message": "Код для авторизации создан", "phone_number": phone_number, "auth_code": auth_code.code})


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = ''.join(re.findall(r"\d+", request.data.get('phone_number', '')))
        user_auth_code = request.data.get('auth_code')

        print(phone_number, user_auth_code)
        if not phone_number or not user_auth_code:
            return Response({"message": "Не передан номер телефона или код авторизации!"},
                            status=status.HTTP_400_BAD_REQUEST)

        auth_code_from_db = AuthSessionModel.objects.filter(phone_number=phone_number,
                                                            expires_at__gt=datetime.now(UTC), is_used=False).first()

        if auth_code_from_db and user_auth_code == auth_code_from_db.code:
            auth_code_from_db.is_used = True
            invite_code = InviteCodeModel.generate_unique_code()
            user, create = UserModel.objects.get_or_create(phone_number=phone_number )
            try:
                InviteCodeModel.objects.get_or_create(code=invite_code, user_id=user.id )
            except IntegrityError:
                _invite_code = InviteCodeModel.objects.get(user_id=user.id )
                print("_invite_code", _invite_code)
            auth_code_from_db.save()

            return Response({
                "message": f"Авторизация пройдена успешно {phone_number}. {auth_code_from_db.code}, {auth_code_from_db.expires_at}"})
        else:
            return Response({
                                "message": "Cрок действия кода истек или код был использован. Отправьте запрос повторно для генерации кода."})


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        phone_number = ''.join(re.findall(r"\d+", request.GET.get('phone_number', '')))
        if not phone_number:
            Response({"message": "Номер телефона не передан!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserModel.objects.get(phone_number=phone_number)
        except UserModel.DoesNotExist:
            return Response({"message": "Пользователь не найден!"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": f"Пользователь найден: {user.phone_number}", "user":UserProfileSerializer(user).data}, status=status.HTTP_200_OK)
