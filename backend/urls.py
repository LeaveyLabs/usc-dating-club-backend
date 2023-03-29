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

from users.views import AcceptMatch, DeleteAccount, ForceCreateMatch, GetPageOrder, PostSurveyAnswers, RegisterUser, SendEmailCode, SendPhoneCode, StopLocationSharing, UpdateLocation, UpdateMatchableStatus, VerifyEmailCode, VerifyPhoneCode
from users.viewsets import BannedEmailViewset, InterestViewset, MessageViewset, NumericalQuestionViewset, TextQuestionViewset, UserViewset, MatchViewset, QuestionViewset, NumericalResponseViewset, TextResponseViewset, WaitingEmailViewset

router = routers.DefaultRouter()
router.register("devices", APNSDeviceAuthorizedViewSet)
router.register("users", UserViewset)
router.register("matches", MatchViewset)
router.register("questions", QuestionViewset)
router.register("numerical-questions", NumericalQuestionViewset)
router.register("text-questions", TextQuestionViewset)
router.register("numerical-responses", NumericalResponseViewset)
router.register("text-responses", TextResponseViewset)
router.register("waiting-emails", WaitingEmailViewset)
router.register("banned-emails", BannedEmailViewset)
router.register("messages", MessageViewset)
router.register("interests", InterestViewset)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication
    path("send-email-code/", SendEmailCode.as_view()),
    path("verify-email-code/", VerifyEmailCode.as_view()),
    path("send-phone-code/", SendPhoneCode.as_view()),
    path("verify-phone-code/", VerifyPhoneCode.as_view()),
    path("register-user/", RegisterUser.as_view()),
    path("post-survey-answers/", PostSurveyAnswers.as_view()),
    path("update-location/", UpdateLocation.as_view()),
    path("delete-account/", DeleteAccount.as_view()),
    path("update-matchable-status/", UpdateMatchableStatus.as_view()),
    path("accept-match/", AcceptMatch.as_view()),
    path("get-page-order/", GetPageOrder.as_view()),
    path("force-create-match/", ForceCreateMatch.as_view()),
    path("stop-sharing-location/", StopLocationSharing.as_view())
]

# Devices
urlpatterns += router.urls
