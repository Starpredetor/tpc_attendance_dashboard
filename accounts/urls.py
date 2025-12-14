from django.urls import path
from .views import login_view, admin_dashboard, volunteer_dashboard, logout_view, dashboard_redirect

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_redirect, name="dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/volunteer/", volunteer_dashboard, name="volunteer_dashboard"),
]