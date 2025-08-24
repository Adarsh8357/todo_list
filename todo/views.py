from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Task
from django.utils import timezone

# -------------------
# User Authentication
# -------------------

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')


# -------------------
# Todo App Views
# -------------------

@login_required(login_url='login')
def index(request):
    tasks = Task.objects.filter(user=request.user, completed=False, deleted=False)
    completed_tasks = Task.objects.filter(user=request.user, completed=True)
    deleted_tasks = Task.objects.filter(user=request.user, deleted=True)

    return render(request, 'todo/index.html', {
        'tasks': tasks,
        'completed_tasks': completed_tasks,
        'deleted_tasks': deleted_tasks,
    })


@login_required(login_url='login')
def add_task(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST.get('description', '')
        due_date = request.POST.get('due_date', None)
        if due_date:
            due_date = timezone.datetime.fromisoformat(due_date)
        Task.objects.create(user=request.user, title=title, description=description, due_date=due_date)
    return redirect('index')


@login_required(login_url='login')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == "POST":
        task.title = request.POST['title']
        task.description = request.POST.get('description', '')
        due_date = request.POST.get('due_date', None)
        if due_date:
            task.due_date = timezone.datetime.fromisoformat(due_date)
        else:
            task.due_date = None
        task.save()
        return redirect('index')
    return render(request, 'todo/edit_task.html', {'task': task})


@login_required(login_url='login')
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = True
    task.save()
    return redirect('index')


@login_required(login_url='login')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.deleted = True
    task.save()
    return redirect('index')


@login_required(login_url='login')
def undo_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.deleted = False
    task.save()
    return redirect('index')
