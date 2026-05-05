from django.db import models

from users.models import CustomUser


# Create your models here.

class Stage(models.Model):
    name = models.CharField(max_length=50,unique=True)
    leaders = models.ManyToManyField(
    "users.CustomUser",
    blank=True,
    related_name="managed_stages"
)

    def __str__(self):
        return self.name

class Family(models.Model):
    name = models.CharField(max_length=50)
    year = models.CharField(max_length=100) 
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="families",null=True,blank=True)
