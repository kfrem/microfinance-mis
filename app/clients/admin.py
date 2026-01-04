from django.contrib import admin
from .models import Client
from audit.models import AuditLog


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'full_name', 'client_type', 'phone', 'risk_category', 'status', 'kyc_verified', 'created_at')
    list_filter = ('client_type', 'risk_category', 'status', 'kyc_verified', 'created_at')
    search_fields = ('client_id', 'full_name', 'phone', 'email', 'ghana_card_id')
    readonly_fields = ('client_id', 'created_at', 'updated_at', 'created_by')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('client_id', 'client_type', 'full_name', 'status')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'address')
        }),
        ('KYC Information', {
            'fields': ('ghana_card_id', 'date_of_birth', 'occupation', 'employer', 'monthly_income')
        }),
        ('Risk & Compliance', {
            'fields': ('risk_category', 'kyc_verified', 'kyc_verified_date', 'kyc_verified_by')
        }),
        ('Group Information', {
            'fields': ('group_size', 'group_leader'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Override to create audit log on save."""
        action = AuditLog.Action.UPDATE if change else AuditLog.Action.CREATE
        
        # Capture changes for UPDATE
        changes = {}
        if change:
            for field in form.changed_data:
                old_value = form.initial.get(field)
                new_value = form.cleaned_data.get(field)
                changes[field] = {
                    'old': str(old_value) if old_value is not None else None,
                    'new': str(new_value) if new_value is not None else None,
                }
        
        # Save the object first
        super().save_model(request, obj, form, change)
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action=action,
            app_label='clients',
            model_name='Client',
            object_id=str(obj.pk),
            object_repr=str(obj),
            changes=changes if changes else None,
            message=f"{'Updated' if change else 'Created'} client: {obj.full_name}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )

    def delete_model(self, request, obj):
        """Override to create audit log on delete."""
        # Store object info before deletion
        object_repr = str(obj)
        object_id = str(obj.pk)
        
        # Delete the object
        super().delete_model(request, obj)
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.DELETE,
            app_label='clients',
            model_name='Client',
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted client: {object_repr}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )

    def delete_queryset(self, request, queryset):
        """Override to create audit logs on bulk delete."""
        # Store info about objects before deletion
        objects_info = [(str(obj.pk), str(obj)) for obj in queryset]
        
        # Delete the queryset
        super().delete_queryset(request, queryset)
        
        # Create audit logs for each deleted object
        for object_id, object_repr in objects_info:
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.DELETE,
                app_label='clients',
                model_name='Client',
                object_id=object_id,
                object_repr=object_repr,
                message=f"Bulk deleted client: {object_repr}",
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            )
