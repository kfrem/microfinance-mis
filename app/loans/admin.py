from django.contrib import admin
from django.utils.html import format_html
from .models import LoanProduct, Loan, LoanSchedule
from audit.models import AuditLog


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'interest_rate', 'interest_method', 'repayment_frequency', 'min_amount', 'max_amount', 'is_active')
    list_filter = ('is_active', 'interest_method', 'repayment_frequency')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Loan Limits', {
            'fields': ('min_amount', 'max_amount', 'min_term_months', 'max_term_months')
        }),
        ('Interest Configuration', {
            'fields': ('interest_rate', 'interest_method', 'repayment_frequency')
        }),
        ('Fees', {
            'fields': ('processing_fee_percentage', 'insurance_fee_percentage', 'late_payment_penalty_rate')
        }),
        ('Requirements', {
            'fields': ('requires_collateral', 'requires_guarantor', 'min_guarantors')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class LoanScheduleInline(admin.TabularInline):
    model = LoanSchedule
    extra = 0
    can_delete = False
    readonly_fields = ('installment_number', 'due_date', 'principal_due', 'interest_due', 'total_due', 
                       'principal_paid', 'interest_paid', 'total_paid', 'balance_due', 'is_paid', 'days_late')
    fields = ('installment_number', 'due_date', 'principal_due', 'interest_due', 'total_due', 
              'principal_paid', 'interest_paid', 'total_paid', 'balance_due', 'is_paid')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'client', 'product', 'principal', 'interest_rate', 'term_months', 
                    'status', 'classification', 'days_in_arrears', 'disbursed_date', 'outstanding_display')
    list_filter = ('status', 'classification', 'interest_method', 'repayment_frequency', 'product', 
                   'disbursed_date', 'application_date')
    search_fields = ('loan_id', 'client__full_name', 'client__client_id')
    readonly_fields = ('loan_id', 'total_interest', 'total_repayable', 'installment_amount', 
                       'created_at', 'updated_at', 'approved_by', 'disbursed_by', 
                       'outstanding_display', 'arrears_display')
    date_hierarchy = 'application_date'
    raw_id_fields = ('client',)
    inlines = [LoanScheduleInline]
    
    fieldsets = (
        ('Loan Identification', {
            'fields': ('loan_id', 'client', 'product', 'status', 'classification')
        }),
        ('Loan Terms', {
            'fields': ('principal', 'interest_rate', 'interest_method', 'term_months', 
                       'repayment_frequency', 'processing_fee', 'insurance_fee')
        }),
        ('Calculated Amounts', {
            'fields': ('total_interest', 'total_repayable', 'installment_amount', 
                       'outstanding_display', 'arrears_display'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('application_date', 'approved_date', 'disbursed_date', 
                       'first_repayment_date', 'maturity_date')
        }),
        ('Disbursement Details', {
            'fields': ('disbursement_method', 'disbursement_reference', 'disbursed_by'),
            'classes': ('collapse',)
        }),
        ('Status & Tracking', {
            'fields': ('days_in_arrears', 'approved_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['generate_schedules', 'recalculate_loan_amounts', 'mark_as_active']
    
    def outstanding_display(self, obj):
        if obj.pk:
            outstanding = obj.get_outstanding_balance()
            color = 'red' if outstanding > 0 else 'green'
            return format_html('<span style="color: {};">GHS {:,.2f}</span>', color, outstanding)
        return '-'
    outstanding_display.short_description = 'Outstanding Balance'
    
    def arrears_display(self, obj):
        if obj.pk and obj.status == 'active':
            arrears = obj.get_arrears_amount()
            if arrears > 0:
                return format_html('<span style="color: red; font-weight: bold;">GHS {:,.2f}</span>', arrears)
            return format_html('<span style="color: green;">GHS 0.00</span>')
        return '-'
    arrears_display.short_description = 'Arrears'
    
    def generate_schedules(self, request, queryset):
        count = 0
        for loan in queryset:
            if loan.disbursed_date:
                loan.generate_repayment_schedule()
                count += 1
        self.message_user(request, f'Generated repayment schedules for {count} loans.')
    generate_schedules.short_description = 'Generate repayment schedules'
    
    def recalculate_loan_amounts(self, request, queryset):
        count = 0
        for loan in queryset:
            loan.calculate_loan_amounts()
            loan.save()
            count += 1
        self.message_user(request, f'Recalculated amounts for {count} loans.')
    recalculate_loan_amounts.short_description = 'Recalculate loan amounts'
    
    def mark_as_active(self, request, queryset):
        count = queryset.filter(status='approved', disbursed_date__isnull=False).update(status='active')
        self.message_user(request, f'Marked {count} loans as active.')
    mark_as_active.short_description = 'Mark as active (if disbursed)'
    
    def save_model(self, request, obj, form, change):
        """Override to create audit log and auto-generate schedule."""
        action = AuditLog.Action.UPDATE if change else AuditLog.Action.CREATE
        
        # Capture changes for UPDATE
        changes = {}
        if change:
            for field in form.changed_data:
                old_value = form.initial.get(field)
                new_value = form.cleaned_data.get(field)
                if field == 'client':
                    changes[field] = {
                        'old': str(old_value) if old_value else None,
                        'new': str(new_value) if new_value else None,
                    }
                else:
                    changes[field] = {
                        'old': str(old_value) if old_value is not None else None,
                        'new': str(new_value) if new_value is not None else None,
                    }
        
        # Save the object first
        super().save_model(request, obj, form, change)
        
        # Generate schedule if disbursed
        if obj.disbursed_date and obj.status in ['active', 'approved']:
            if not obj.schedule_entries.exists() or 'disbursed_date' in form.changed_data:
                obj.generate_repayment_schedule()
        
        # Create audit log
        AuditLog.objects.create(
            user=request.user,
            action=action,
            app_label='loans',
            model_name='Loan',
            object_id=str(obj.pk),
            object_repr=str(obj),
            changes=changes if changes else None,
            message=f"{'Updated' if change else 'Created'} loan {obj.loan_id} for {obj.client.full_name}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )
    
    def delete_model(self, request, obj):
        """Override to create audit log on delete."""
        object_repr = str(obj)
        object_id = str(obj.pk)
        
        super().delete_model(request, obj)
        
        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.DELETE,
            app_label='loans',
            model_name='Loan',
            object_id=object_id,
            object_repr=object_repr,
            message=f"Deleted loan: {object_repr}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )
    
    def delete_queryset(self, request, queryset):
        """Override to create audit logs on bulk delete."""
        objects_info = [(str(obj.pk), str(obj)) for obj in queryset]
        
        super().delete_queryset(request, queryset)
        
        for object_id, object_repr in objects_info:
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.DELETE,
                app_label='loans',
                model_name='Loan',
                object_id=object_id,
                object_repr=object_repr,
                message=f"Bulk deleted loan: {object_repr}",
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            )


@admin.register(LoanSchedule)
class LoanScheduleAdmin(admin.ModelAdmin):
    list_display = ('loan', 'installment_number', 'due_date', 'total_due', 'total_paid', 
                    'balance_due', 'is_paid', 'days_late_display')
    list_filter = ('is_paid', 'due_date')
    search_fields = ('loan__loan_id', 'loan__client__full_name')
    readonly_fields = ('loan', 'installment_number', 'due_date', 'principal_due', 'interest_due', 
                       'total_due', 'principal_balance', 'created_at', 'updated_at')
    date_hierarchy = 'due_date'
    
    def days_late_display(self, obj):
        if obj.days_late > 0:
            return format_html('<span style="color: red; font-weight: bold;">{} days</span>', obj.days_late)
        return '0 days'
    days_late_display.short_description = 'Days Late'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
