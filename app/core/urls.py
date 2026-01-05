from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    path("", home, name='home'),  # Home page with all dashboard links
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("reports/", include("reports.urls")),
    path("management/", include("management_reports.urls")),
]
