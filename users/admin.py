from django.contrib import admin

from users.models import CustomUser
from django.contrib import admin
from django.contrib.auth import get_user_model
from axes.models import AccessAttempt
from axes.admin import AccessAttemptAdmin

User = get_user_model()

admin.site.unregister(AccessAttempt)


class CustomAccessAttemptAdmin(AccessAttemptAdmin):
    list_display = list(AccessAttemptAdmin.list_display) + ['get_full_name']

    def get_full_name(self, obj):
        user = User.objects.filter(username=obj.username).first()
        return user.full_name if user else "-"
    get_full_name.short_description = "Full Name"


admin.site.register(AccessAttempt, CustomAccessAttemptAdmin)
# Register your models here.
admin.site.register(CustomUser)