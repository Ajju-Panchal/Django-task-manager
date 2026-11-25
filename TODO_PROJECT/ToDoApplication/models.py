from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=32)

    def __str__(self):
        return f"Profile for {self.user.username}"


class Task(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    )
    PRIORITY_CHOICES = (
        ("1", "High Priority"),
        ("2", "Medium Priority"),
        ("3", "Low Priority"),
    )
    task_title = models.CharField(max_length=200)
    task_description = models.TextField(blank=True)
    task_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="3")

    def __str__(self):
        return self.task_title
