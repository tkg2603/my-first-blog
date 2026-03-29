from django.contrib import admin
from .models import Task, Family, User

admin.site.register(Task)
admin.site.register(Family)
admin.site.register(User)