from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, User, Family, UserTask

# Create your views here.
def welcome(request):
    return render(request, 'tasks/welcome.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if not username:
            return render(request, 'tasks/register.html', {
                'error': 'ユーザー名を入力してください'
            })
        
        if not password:
            return render(request, 'tasks/register.html', {
                'error': 'パスワードを入力してください'
            })

        if password != password_confirm:
            return render(request, 'tasks/register.html', {
                'error': 'パスワードが一致しません'
            })
        if User.objects.filter(username=username).exists():
            return render(request, 'tasks/register.html', {
                'error': 'このユーザー名はすでに使われています'
            })


        role = request.POST.get("role")
        family_name = request.POST.get("family_name")
        family_code = request.POST.get("family_code")

        if role in ['mama', 'papa']:
            if not family_name:
                return render(request, 'tasks/register.html', {
                  'error': 'ファミリー名を入力してください'
                 })
            family = Family.objects.create(name=family_name)

        else:
            if not family_code:
                return render(request, 'tasks/register.html', {
                    'error': 'ファミリーコードを入力してください'
                 })
            try:
                family = Family.objects.get(code=family_code)
            except Family.DoesNotExist:
                return render(request, 'tasks/register.html', {
                    'error': 'ファミリーコードが正しくありません'
                })

        user = User.objects.create_user(
            username=username,
            password=password,
            role=role,
            family=family,
        )
        return redirect("login")
    
    return render(request, 'tasks/register.html')

@login_required
def task_list(request):
    tasks = Task.objects.filter(
        user_tasks__user__family=request.user.family
        ).distinct()
    child_count = User.objects.filter(
        family=request.user.family,
        role='child'
    ).count()
    return render(request, 'tasks/task_list.html', {
        'tasks':tasks,
        'child_count': child_count
        })

@login_required
def task_create(request):
    if request.method == "POST":
         title = request.POST.get("title")
         priority = request.POST.get("priority")
         due_date = request.POST.get("due_date")
         task = Task.objects.create(
             title=title,
             priority=priority,
             due_date=due_date if due_date else None,
             )
         
         family_members = User.objects.filter(family=request.user.family)
         for member in family_members:
             UserTask.objects.create(user=member, task=task)
         request.user.family,
         return redirect("home")
    return render(request, "tasks/task_create.html")

@login_required   
def task_delete(request, task_id):
    if request.user.role not in ['mama', 'papa']:
        return redirect('home')
    task = Task.objects.get(id=task_id)
    task.delete()   
    
    return redirect("home")

@login_required
def task_edit(request, task_id):
    
    task = Task.objects.get(id=task_id)


    if request.method == "POST":
        task.title = request.POST.get("title")
        task.priority = request.POST.get("priority")
        task.due_date = request.POST.get("due_date") or None
        task.status = request.POST.get("status")
        task.save()
        return redirect("home")
    return render(request,"tasks/task_edit.html", {"task": task})

@login_required    
def home(request):
    if not request.user.family:
        return redirect('register')

    tasks = Task.objects.filter(
        user_tasks__user__family=request.user.family
        ).distinct().order_by('due_date')

    
    if request.user.role in ['mama', 'papa']:
        return render (request, 'tasks/parent_home.html',
                        {'tasks': tasks,
                         'family_code': request.user.family.code,
                         'family_name': request.user.family.name,
                         })
    else:
        return render(request,'tasks/child_home.html', {
            'tasks': tasks,
            'family_name':request.user.family.name,
            })
    
@login_required
def past_tasks(request):
    tasks = Task.objects.filter(
        user_tasks__user__family=request.user.family,
        status='done'
    ).distinct()
    return render(request, 'tasks/past_tasks.html', {'tasks': tasks})

@login_required
def task_complete(request, task_id):
    task = Task.objects.get(id=task_id)
    task.status = 'done'
    task.completed_by = request.user
    task.save()
    return redirect('home')
    