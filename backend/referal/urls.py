from django.urls import path, include, re_path

from referal.views import InviteCodeView, RequestCodeView, VerifyCodeView


urlpatterns = [
    # path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('admin/', admin.site.urls),
    path('invite_code/', InviteCodeView.as_view(), name='invite_code'),
    path('mobile_login/', RequestCodeView.as_view(), name='register'),
    path('verify_login/', VerifyCodeView.as_view(), name='verify'),


]