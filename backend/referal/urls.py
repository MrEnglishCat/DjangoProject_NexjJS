from django.urls import path, include, re_path

from referal.views import RequestCodeView, VerifyCodeView, UserProfileView, ActivateInviteCodeView, \
    UserProfileEditView, GenerateInviteCodeView
from rest_framework.routers import DefaultRouter

routerInviteCodes = DefaultRouter()
routerInviteCodes.register(r'generate_invite', GenerateInviteCodeView, basename='generate_invite')


urlpatterns = [
    path('mobile_login/', RequestCodeView.as_view(), name='register'),
    path('verify_code/', VerifyCodeView.as_view(), name='verify'),
    path('user_profile/<str:phone_number>/', UserProfileView.as_view(), name='user_profile'),
    path('user_profile/update/<int:pk>/', UserProfileEditView.as_view(), name='user_profile_edit'),
    path('activate_invite/', ActivateInviteCodeView.as_view(), name='activate_invite'),
    path('', include(routerInviteCodes.urls)),

]
