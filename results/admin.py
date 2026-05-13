from django.contrib import admin

from results.models import Exam, Result, Subject

# Register your models here.
admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Result)