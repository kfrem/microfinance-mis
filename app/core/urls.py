from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("reports/", include("reports.urls")),
    path("management/", include("management_reports.urls")),
]
