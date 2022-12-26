"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet
from rest_framework import routers

from users.views import DeleteAccount, MatchUsers, PostSurveyAnswers, RegisterUser, SendEmailCode, SendPhoneCode, UpdateLocation, VerifyEmailCode, VerifyPhoneCode

router = routers.DefaultRouter()
router.register("devices", APNSDeviceAuthorizedViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication
    path("send-email-code/", SendEmailCode.as_view()),
    path("verify-email-code/", VerifyEmailCode.as_view()),
    path("send-phone-code", SendPhoneCode.as_view()),
    path("verify-phone-code/", VerifyPhoneCode.as_view()),
    path("register-user/", RegisterUser.as_view()),
    path("post-survey-answers/", PostSurveyAnswers.as_view()),
    path("update-location/", UpdateLocation.as_view()),
    path("match-users", MatchUsers.as_view()),
    path("delete-account/", DeleteAccount.as_view()),
]

# Devices
urlpatterns += router.urls
