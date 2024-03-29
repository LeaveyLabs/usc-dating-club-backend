from django.contrib import admin

from users.models import BannedEmail, Category, EmailAuthentication, Interest, NumericalQuestion, PhoneAuthentication, TextAnswerChoice, TextQuestion, User, Match, Notification, NumericalResponse, TextResponse, BaseQuestion, WaitingEmail, Message

admin.site.register(User)

@admin.register(
    EmailAuthentication, 
    PhoneAuthentication, 
    Match, 
    Notification, 
    NumericalResponse,
    TextResponse,
    Category,
    BaseQuestion,
    NumericalQuestion,
    TextQuestion,
    TextAnswerChoice,
    WaitingEmail,
    BannedEmail,
    Message,
    Interest)
class UniversalAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]