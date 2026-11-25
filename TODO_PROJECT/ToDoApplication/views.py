from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import Task, UserProfile


@login_required(login_url="login")
def index(request):
    return render(request, "ToDoList.html")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            messages.error(request, "Please fill in all fields.")
            return redirect("login")
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
        login(request, user)
        return redirect("index")
    if request.user.is_authenticated:
        return redirect("index")
    return render(request, "userLogin.html")


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "GET":
        return render(request, "userRegistration.html")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("password1", "")
    email = request.POST.get("email", "").strip()
    phone = request.POST.get("phone", "").strip()
    if not all((username, password, confirm_password, email, phone)):
        messages.error(request, "Please fill in all fields.")
        return redirect("register")
    if password != confirm_password:
        messages.error(request, "Passwords do not match.")
        return redirect("register")
    if User.objects.filter(username=username).exists():
        messages.error(request, "Username already exists.")
        return redirect("register")
    if User.objects.filter(email=email).exists():
        messages.error(request, "Email already exists.")
        return redirect("register")

    user = User.objects.create_user(username=username, password=password, email=email)
    UserProfile.objects.create(user=user, phone=phone)
    login(request, user)
    return redirect("index")


@login_required(login_url="login")
@require_GET
def get_task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by("task_priority", "id")
    return JsonResponse({"tasks": [{
        "id": task.id,
        "task_title": task.task_title,
        "task_status": task.get_task_status_display(),
        "task_priority": task.get_task_priority_display(),
        "task_description": task.task_description,
    } for task in tasks]})


@login_required(login_url="login")
@require_POST
def add_task(request):
    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    priority = request.POST.get("priority", "")
    errors = {}
    if not title:
        errors["title"] = "Title is required."
    elif len(title) > 200:
        errors["title"] = "Title must be 200 characters or fewer."
    if priority not in dict(Task.PRIORITY_CHOICES):
        errors["priority"] = "Choose a valid priority."
    if errors:
        return JsonResponse({"errors": errors}, status=400)
    Task.objects.create(user=request.user, task_title=title, task_description=description, task_priority=priority)
    return JsonResponse({"message": "Task added successfully."}, status=201)


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def get_or_edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == "GET":
        return JsonResponse({
            "title": task.task_title,
            "description": task.task_description,
            "priority": task.task_priority,
            "status": task.task_status,
        })
    title = request.POST.get("title", "").strip()
    description = request.POST.get("description", "").strip()
    priority = request.POST.get("priority", "")
    status = request.POST.get("status", "")
    errors = {}
    if not title:
        errors["title"] = "Title is required."
    elif len(title) > 200:
        errors["title"] = "Title must be 200 characters or fewer."
    if priority not in dict(Task.PRIORITY_CHOICES):
        errors["priority"] = "Choose a valid priority."
    if status not in dict(Task.STATUS_CHOICES):
        errors["status"] = "Choose a valid status."
    if errors:
        return JsonResponse({"errors": errors}, status=400)
    task.task_title = title
    task.task_description = description
    task.task_priority = priority
    task.task_status = status
    task.save(update_fields=["task_title", "task_description", "task_priority", "task_status"])
    return JsonResponse({"message": "Task updated successfully."})


@login_required(login_url="login")
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return JsonResponse({"message": "Task deleted successfully."})


@login_required(login_url="login")
@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


def _filtered_tasks(user, **filters):
    tasks = Task.objects.filter(user=user, **filters).order_by("task_priority", "id")
    return [{
        "id": task.id,
        "task_title": task.task_title,
        "task_description": task.task_description,
        "task_status": task.get_task_status_display(),
        "task_priority": task.get_task_priority_display(),
    } for task in tasks]


@login_required(login_url="login")
@require_GET
def filter_by_priority(request):
    priority = request.GET.get("priority", "")
    if priority == "0":
        return JsonResponse({"tasks": _filtered_tasks(request.user)})
    if priority not in dict(Task.PRIORITY_CHOICES):
        return JsonResponse({"error": "Invalid priority value."}, status=400)
    return JsonResponse({"tasks": _filtered_tasks(request.user, task_priority=priority)})


@login_required(login_url="login")
@require_GET
def filter_by_status(request):
    status = request.GET.get("status", "")
    if status == "0":
        return JsonResponse({"tasks": _filtered_tasks(request.user)})
    if status not in dict(Task.STATUS_CHOICES):
        return JsonResponse({"error": "Invalid status value."}, status=400)
    return JsonResponse({"tasks": _filtered_tasks(request.user, task_status=status)})
