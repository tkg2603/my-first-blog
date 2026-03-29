from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register, name='register'),
    path('task_list/', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path("delete/<int:task_id>/", views.task_delete, name="task_delete"),
    path("edit/<int:task_id>/", views.task_edit, name="task_edit"), 

    path('login/', auth_views.LoginView.as_view(template_name='tasks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
         
    path('home/', views.home, name='home'),
    path('past_tasks/', views.past_tasks, name='past_tasks'),
    path('complete/<int:task_id>/', views.task_complete, name='task_complete'),
]