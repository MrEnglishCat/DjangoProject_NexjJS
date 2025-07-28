import re
import time
from datetime import datetime, UTC

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from mimesis import Person
from rest_framework import status
from rest_framework.generics import UpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response  # Не забудьте импортировать Response
from referal.models import AuthSessionModel, UserModel, InviteCodeModel, InviteCodeUsageModel
from referal.serializers import UserProfileSerializer, InviteCodeSerializer, InviteCodeUsageSerializer, \
    ActivateInviteCodeSerializer, UserProfileEditSerializer


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

            person = Person()
            try:
                user, create = UserModel.objects.get_or_create(
                    phone_number=phone_number,
                    first_name=person.first_name(),
                    username=person.username(),
                    email=person.email(),
                )
            except IntegrityError:
                user = UserModel.objects.get(phone_number=phone_number)

            if not (InviteCodeModel.objects.filter(user_id=user.id, is_active=True)):
                try:
                    _invite_code_obj, create = InviteCodeModel.objects.get_or_create(invite_code=invite_code,
                                                                                     user_id=user.id,
                                                                                     is_active=True)
                    InviteCodeUsageModel.objects.get_or_create(invite_code=_invite_code_obj, user_id=user.id)
                except IntegrityError:
                    _invite_code = InviteCodeModel.objects.get(user_id=user.id, is_active=True)

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


class UserProfileEditView(UpdateAPIView):
    permission_classes = [AllowAny]

    queryset = UserModel.objects.all()
    # serializer_class = UserProfileSerializer
    serializer_class = UserProfileEditSerializer


class ActivateInviteCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        invite_code_obj = ActivateInviteCodeSerializer(
            data=request.data
        )
        if invite_code_obj.is_valid():
            _invite_code_model = invite_code_obj.data
            # invite_code_db = InviteCodeModel.objects.get(invite_code=_invite_code)
            # TODO дописать метод активации
            return Response({
                "success": True,
                "message": "Инвайт код активирован!"
            })


        else:
            return Response({
                "success": False,
                "message": "Переданы невалидные данные!",
                "errors": invite_code_obj.errors

            }, status=400)


class GenerateInviteCodeView(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        # Логика для POST /generate_invite/
        # Создание нового инвайт-кода


        print(request.data)

        new_invite_code = InviteCodeModel.generate_unique_code()
        _invite_code_obj = InviteCodeModel(invite_code=new_invite_code, is_active=False)
        print(new_invite_code)
        return Response({
            "success": True,
            "message": "Инвайт-код сгенерирован",
            "invite_code": new_invite_code
        })

    def list(self, request):
        # Логика для GET /generate_invite/
        # Получение списка всех инвайт-кодов (если нужно)
        _invite_codes = InviteCodeModel.objects.filter(is_active=False, user_id=None)
        return Response({
            "success": True,
            "message": "Инвайт-коды загружены",
            "invite_codes": InviteCodeSerializer(_invite_codes, many=True).data
        })

    def retrieve(self, request, pk=None):
        # Логика для GET /generate_invite/{pk}/
        # Получение конкретного инвайт-кода по ID
        pass

    def destroy(self, request, pk=None):
        # Логика для DELETE /generate_invite/{pk}/
        # Удаление конкретного инвайт-кода по ID
        pass




