"""
URL configuration for tpc_attendance_dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path


class SuperUserAdminSite(admin.AdminSite):
    """Custom admin site that only allows superusers"""
    
    def has_permission(self, request):
        """Only allow superusers to access the admin panel"""
        return request.user.is_active and request.user.is_superuser


# Create custom admin site instance
admin_site = SuperUserAdminSite(name='superadmin')

# Re-register all models from the default admin site to the custom one
admin_site._registry = admin.site._registry.copy()

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('accounts.urls')),
    path("audit-logs/", include("auditlog.urls")),
    path("lectures/", include("lectures.urls")),
    path('attendance/', include('attendance.urls')),
    path('students/', include('students.urls')),
    path('reports/', include('reports.urls')),
    path('notifications/', include('notifications.urls'))
]
