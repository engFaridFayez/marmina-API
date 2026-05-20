from django.db import models

from users.models import CustomUser

# Create your models here.
class ActivityLog(models.Model):
    ACTION_TYPES = [
        ("create", "Create"),
        ("update", "Update"),
        ("unblock", "Unblock"),
        ("block", "Block"),
        ("login", "Login"),
        ("other", "Other"),
    ]

    actor = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,related_name="actions_performed")
    target_user = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True,related_name="actions_received")

    action = models.CharField(max_length=30,choices=ACTION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]