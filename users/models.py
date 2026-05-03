from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


ROLES = [
    ('مخدوم','مخدوم'),
    ('خادم عادي','خادم عادي'),
    ('امين مساعد اسرة','امين مساعد اسره'),
    ('امين اسرة','امين اسرة'),
    ('امين مرحلة','امين مرحلة'),
    ('امين الشمامسة','امين الشمامسة'),
]
class CustomUser(AbstractUser):
    required_password_change = models.BooleanField(default=False)
    role = models.CharField(choices=ROLES,default="مخدوم")
    password_change_date = models.DateTimeField(_('Password change date'),default=timezone.now)
