from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "user",
        "ip_address",
    )
    list_filter = ("action", "app_label", "model_name", "created_at")
    search_fields = (
        "object_id",
        "object_repr",
        "message",
        "user__username",
        "user_agent",
        "ip_address",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    # keep audit immutable in Admin
    readonly_fields = (
        "created_at",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "changes",
        "message",
        "ip_address",
        "user_agent",
        "user",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
