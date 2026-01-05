from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "colored_action",
        "record_info",
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
    list_per_page = 50

    # keep audit immutable in Admin
    readonly_fields = (
        "created_at",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "formatted_changes",
        "message",
        "ip_address",
        "user_agent",
        "user",
    )
    
    fieldsets = (
        ('Action Details', {
            'fields': ('created_at', 'action', 'user', 'ip_address')
        }),
        ('Record Information', {
            'fields': ('app_label', 'model_name', 'object_id', 'object_repr')
        }),
        ('Changes & Details', {
            'fields': ('formatted_changes', 'message'),
            'classes': ('collapse',)
        }),
        ('Technical Info', {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
    )

    def colored_action(self, obj):
        """Display action with color coding."""
        colors = {
            'CREATE': '#28a745',  # Green
            'UPDATE': '#ffc107',  # Yellow
            'DELETE': '#dc3545',  # Red
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<strong style="color: {};">{}</strong>',
            color,
            obj.action
        )
    colored_action.short_description = 'Action'
    
    def record_info(self, obj):
        """Display combined record information."""
        return format_html(
            '<strong>{}</strong><br><small>{} (ID: {})</small>',
            obj.object_repr or 'N/A',
            f"{obj.app_label}.{obj.model_name}",
            obj.object_id or 'N/A'
        )
    record_info.short_description = 'Record'
    
    def formatted_changes(self, obj):
        """Display changes in readable format."""
        if obj.changes:
            import json
            try:
                changes_dict = json.loads(obj.changes) if isinstance(obj.changes, str) else obj.changes
                formatted = '<ul>'
                for field, (old, new) in changes_dict.items():
                    formatted += f'<li><strong>{field}:</strong> "{old}" → "{new}"</li>'
                formatted += '</ul>'
                return format_html(formatted)
            except:
                return obj.changes
        return 'No changes recorded'
    formatted_changes.short_description = 'Changes'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow superusers to delete old audit logs
        return request.user.is_superuser
