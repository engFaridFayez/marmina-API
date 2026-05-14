from django.db import models

from results.models import Exam
from users.models import CustomUser

# Create your models here.
class Attendance(models.Model):
    student = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="attendances")
    term = models.ForeignKey(Exam,on_delete=models.CASCADE,null=True,blank=True)
    date = models.DateField()
    is_present_mass = models.BooleanField(default=False)
    is_present_family = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student","date")

    def __str__(self):
        return f"{self.student.full_name} - {self.date}"