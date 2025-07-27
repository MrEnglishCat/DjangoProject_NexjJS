from django.urls import path, include, re_path

from referal.views import InviteCodeView, RequestCodeView, VerifyCodeView, UserProfileView, ActivateInviteCodeView

urlpatterns = [
    path('invite_code/', InviteCodeView.as_view(), name='invite_code'),
    path('mobile_login/', RequestCodeView.as_view(), name='register'),
    path('verify_code/', VerifyCodeView.as_view(), name='verify'),
    path('user_profile/<str:phone_number>/', UserProfileView.as_view(), name='user_profile'),
    path('activate_invite/', ActivateInviteCodeView.as_view(), name='activate_invite'),


]