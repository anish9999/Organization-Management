from django.contrib import admin
from organization.models import *
# Register your models here.


@admin.register(OrganizationCategory)
class OrganizationCategoryAdmin(admin.ModelAdmin):
    list_display = ['organization_category', 'updated_at', 'created_at']
    ordering = ('-created_at',)


from django.contrib import admin
from organization.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'created_by',
        'organization_id',
        'organization_category',
        'organization_name',
        'established_date',
        'organization_email',
        'contact_number',
        'country',
        'state',
        'city',
        'street_address',
        'zip_code',
        'updated_at',
        'created_at'
    ]
    ordering = ('-created_at',)
    # list_filter = ['user_unique_id', 'organization_id', 'host_type',
    #                'organization_name', 'phone_number', 'country', 'city']


@admin.register(OrganizationEmployee)
class OrganizationEmployeeAdmin(admin.ModelAdmin):
    list_display = ['added_by','organization_id', 'employee_id', 'position',
                    'organization_joined_date', 'role', 'updated_at', 'added_at', 'is_org_admin']
    ordering = ('-added_at',)
    # list_filter = ['organization_id', 'employee', 'position']


@admin.register(EmployeePermission)
class EmployeePermissionAdmin(admin.ModelAdmin):
    list_display = ['added_by','organization_id', 'employee_id', 'is_org_admin', 'is_list',
                    'is_create', 'is_update', 'is_retrieve', 'is_delete', 'added_at', 'updated_at']

@admin.register(OrganizationExEmployee)
class OrganizationExEmployeeAdmin(admin.ModelAdmin):
    list_display = ['removed_by','organization_id', 'employee_id', 'position',
                    'organization_joined_date', 'role', 'removed_at']
    ordering = ('-removed_at',)


@admin.register(OrganizationNotification)
class OrganizationNotificationAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'permission_notify', 'updated_at']   