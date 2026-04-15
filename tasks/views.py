from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Task, User, Family, UserTask
from itertools import groupby
from django.utils.timezone import localdate

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

        family = None  

        if role in ['mama', 'papa']:
            if family_code:
                # 親でもコードがあれば既存のファミリーを探す（第二登録者パターン）
                try:
                    family = Family.objects.get(code=family_code)
                except Family.DoesNotExist:
                    return render(request, 'tasks/register.html', {
                        'error': 'ファミリーコードが正しくありません'
                    })
            elif family_name:
                # コードがなく、ファミリー名がある場合は新規作成（第一登録者パターン）
                family = Family.objects.create(name=family_name)
            else:
                # どちらも入力がない場合
                return render(request, 'tasks/register.html', {
                    'error': 'ファミリー名またはファミリーコードを入力してください'
                })

        else:  # 子供などの場合
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
        user_tasks__user__family=request.user.family,
        status__in=['todo', 'in_progress']  
    ).distinct().order_by('due_date')

    in_progress_tasks = Task.objects.filter(
        user_tasks__user__family=request.user.family,
        status='in_progress'
    ).distinct().order_by('due_date')


    if request.user.role in ['mama', 'papa']:
        return render (request, 'tasks/parent_home.html',
                        {'tasks': tasks,
                         'in_progress_tasks': in_progress_tasks,
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
    ).distinct().order_by('-due_date')

    grouped_tasks = []
    for date, group in groupby(tasks, key=lambda t: t.due_date.date() if t.due_date else None):
        grouped_tasks.append({
            'date': date,
            'tasks': list(group)
        })

    return render(request, 'tasks/past_tasks.html', {'grouped_tasks': grouped_tasks,})

@login_required
def task_complete(request, task_id):
    task = Task.objects.get(id=task_id)
    task.status = 'done'
    task.completed_by = request.user
    task.save()
    return redirect('home')
    