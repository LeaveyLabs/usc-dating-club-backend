from django.contrib import admin

from users.models import BannedEmail, EmailAuthentication, PhoneAuthentication, User, Match, Notification, NumericalResponse, TextResponse, Question, WaitingEmail

# Register your models here.
# admin.site.register(User)
# admin.site.register(EmailAuthentication)
# admin.site.register(PhoneAuthentication)
# admin.site.register(Match)
# admin.site.register(Notification)
# admin.site.register(NumericalResponse)
# admin.site.register(TextResponse)
# admin.site.register(Question)
# admin.site.register(WaitingEmail)
# admin.site.register(BannedEmail)

@admin.register(
    User, 
    EmailAuthentication, 
    PhoneAuthentication, 
    Match, 
    Notification, 
    NumericalResponse,
    TextResponse,
    Question,
    WaitingEmail,
    BannedEmail)
class UniversalAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]