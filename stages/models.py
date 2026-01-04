from django.db import models

from users.models import CustomUser


# Create your models here.

ROLE = {
    ('خادم عادي','خادم عادي'),
    ('امين مساعد اسرة','امين مساعد اسره'),
    ('امين اسرة','امين اسرة'),
    ('امين مرحلة','امين مرحلة'),
    ('امين الشمامسة','امين الشمامسة'),
}

class Stage(models.Model):
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name

class Family(models.Model):
    name = models.CharField(max_length=50)
    year = models.CharField(max_length=100) 
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="families")

    

class Child(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    birth_date = models.DateField()
    phone = models.CharField(max_length=20)
    parent_phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    father = models.CharField(max_length=50)
    year_of_entrance = models.DateField()
    year_of_graduation = models.DateField(null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        return self.name


class Servant(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    birth_date = models.DateField()
    address = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE, default='خادم عادي')
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True, related_name="servants")
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name="servants")
