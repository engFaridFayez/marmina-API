from django.db import models

from users.models import CustomUser

# Create your models here.
class Subject(models.Model):
    name = models.CharField(max_length=100)
    final_grade = models.IntegerField()
    success_grade = models.IntegerField()

class Exam(models.Model):
    name = models.CharField(max_length=100)
    year = models.CharField(max_length=20)

class Result(models.Model):
    student = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE)
    points = models.FloatField()

    def is_success(self):
        return self.points >= self.subject.success_grade