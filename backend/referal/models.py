from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string


class UserModel(models.Model):
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="Номер телефона")
    username = models.CharField(max_length=30, verbose_name="Username", null=True)
    first_name = models.CharField(max_length=50, verbose_name="Имя", null=True)
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", null=True)
    email = models.EmailField(max_length=50, verbose_name="Email", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")


    def __str__(self):
        return f"UserModel({self.phone_number}, {self.username}, {self.first_name}, {self.created_at}, {self.updated_at})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class AuthSessionModel(models.Model):
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    code = models.CharField(max_length=4, verbose_name="Код подтверждения")
    expires_at = models.DateTimeField(verbose_name="Срок действия")
    is_used = models.BooleanField(default=False, verbose_name="Использован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    @classmethod
    def create_session(cls, phone_number):
        """Создание новой сессии авторизации с 4-значным кодом"""
        code = ''.join(random.choices(string.digits, k=4))
        expires_at = timezone.now() + timedelta(minutes=5)  # Код действует 5 минут
        return cls.objects.create(
            phone_number=phone_number,
            code=code,
            expires_at=expires_at
        )

    def is_valid(self):
        """Проверка валидности сессии"""
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.phone_number}: {self.code}"

    class Meta:
        verbose_name = "Сессия авторизации"
        verbose_name_plural = "Сессии авторизации"


class InviteCodeModel(models.Model):
    invite_code = models.CharField(max_length=6, unique=True, verbose_name="Инвайт-код")
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='own_invite_code',
                               verbose_name="Пользователь", null=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_unique_code()
        super().save(*args, **kwargs)


    @classmethod
    def generate_unique_code(self):
        """Генерация уникального 6-значного инвайт-кода"""
        while True:
            invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not InviteCodeModel.objects.filter(invite_code=invite_code).exists():
                return invite_code

    def __str__(self):
        return f"{self.invite_code} ({self.user.phone_number})"

    class Meta:
        verbose_name = "Инвайт-код"
        verbose_name_plural = "Инвайт-коды"


class InviteCodeUsageModel(models.Model):
    invite_code = models.ForeignKey(InviteCodeModel, on_delete=models.CASCADE, related_name='usages',
                                    verbose_name="Инвайт-код")
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='activated_invites',
                             verbose_name="Пользователь")
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата активации")
    is_revoked = models.BooleanField(default=False, verbose_name="Отозван")

    def __str__(self):
        return f"{self.user.phone_number} -> {self.invite_code.invite_code}"

    class Meta:
        unique_together = ('user', 'invite_code')  # Каждый пользователь может активировать только один код
        verbose_name = "Использование инвайт-кода"
        verbose_name_plural = "Использования инвайт-кодов"