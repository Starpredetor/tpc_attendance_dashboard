from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            elif user.role == "VOLUNTEER":
                return redirect("volunteer_dashboard")

        messages.error(request, "Invalid credentials")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def admin_dashboard(request):
    if request.user.role != "ADMIN":
        return redirect("login")

    return render(request, "dashboards/admin_dashboard.html")


@login_required
def volunteer_dashboard(request):
    if request.user.role != "VOLUNTEER":
        return redirect("login")

    return render(request, "dashboards/volunteer_dashboard.html")
