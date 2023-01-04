from django.contrib import admin

from users.models import EmailAuthentication, PhoneAuthentication, User, Match, Notification

# Register your models here.
admin.site.register(User)
admin.site.register(EmailAuthentication)
admin.site.register(PhoneAuthentication)
admin.site.register(Match)
admin.site.register(Notification)