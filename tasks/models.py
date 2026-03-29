import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser

class Family(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Families"

class User(AbstractUser):
    ROLE_CHOICES= [
        ('mama', 'ママ'),
        ('papa', 'パパ'),
        ('child', '子ども'),
    ]       
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True)
    family=models.ForeignKey(
    Family,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo','まだだよ'),
        ('in_progress','やってるよ'),
        ('done','できたよ'),
    ]
    PRIORITY_CHOICE = [
        ('high','★★★'),
        ('medium','★★'),
        ('low','★'),
    ]

    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_tasks'
    )

   
    title = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICE, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.title
    
class UserTask(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_tasks'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='user_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'task')

    def __str__(self):
        return f"{self.user} - {self.task}"