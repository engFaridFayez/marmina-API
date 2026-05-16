import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

ROLES = [
    ('admin','admin'),
    ('مخدوم','مخدوم'),
    ('خادم عادي','خادم عادي'),
    ('امين مساعد اسرة','امين مساعد اسره'),
    ('امين اسرة','امين اسرة'),
    ('امين مرحلة','امين مرحلة'),
    ('امين الشمامسة','امين الشمامسة'),
]

def upload_path(instance,filename):
    return os.path.join('images','avatars',str(instance.username),filename)
class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20,null=True,blank=True)
    father = models.CharField(max_length=30)
    age = models.IntegerField(null=True,blank=True)
    joined_date = models.DateField(null=True,blank=True)
    birth_date = models.DateField(null=True,blank=True)
    parent_phone = models.CharField(max_length=20,null=True,blank=True)
    role = models.CharField(max_length=50,choices=ROLES,default="مخدوم")
    image = models.ImageField(upload_to=upload_path,blank=True,null=True)
    slogan = models.CharField(max_length=100, default="شاطر",null=True,blank=True)
    family = models.ForeignKey("stages.Family",on_delete=models.SET_NULL,null=True,blank=True)



class StageLeader(models.Model):
    stage = models.ForeignKey("stages.Stage", on_delete=models.DO_NOTHING, db_column="stage_id")
    customuser = models.ForeignKey("users.CustomUser", on_delete=models.DO_NOTHING, db_column="customuser_id")

    class Meta:
        db_table = "stages_stage_leaders"
        managed = False