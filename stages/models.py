from django.db import models


# Create your models here.

class Stage(models.Model):
    name = models.CharField(max_length=50, unique=True)

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
    next_family = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="previous_family")
    drive_folder_id = models.CharField(max_length=255,null=True,blank=True)


    def __str__(self):
        return self.name