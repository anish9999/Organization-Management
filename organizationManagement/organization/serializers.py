from rest_framework import serializers
from organization.models import *
# from organization.utils import generate_id, luhn_algorithm, get_user_details
# from organization.client import UserUniqueIdChecker


from rest_framework import serializers
from organization.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'organization_name',
            'established_date',
            'organization_category',
            'organization_email',
            'contact_number',
            'country',
            'state',
            'city',
            'street_address',
            'zip_code'
        ]



class OrganizationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['created_by', 'organization_name', 'established_date', 'organization_category',
                  'organization_email', 'contact_number', 'country', 'state', 'city', 'street_address', 'zip_code']

        read_only_fields = ['created_by', 'established_date']


class OrganizationEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationEmployee
        fields = ['organization_id', 'employee_id', 'position', 'organization_joined_date', 'is_org_admin']

        read_only_fields = ['is_org_admin', 'organization_id']


class OrganizationEmployeeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationEmployee
        fields = ['organization_id', 'employee_id',
                  'position', 'organization_joined_date', 'role', 'is_org_admin']

        read_only_fields = ['organization_id', 'employee_id', 'is_org_admin']


class OrganizationExEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationExEmployee
        fields = ['organization_id', 'employee_id',
                  'position', 'organization_joined_date', 'role', 'removed_at']


class EmployeePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePermission
        fields = ['organization_id', 'employee_id', 'is_create', 'is_list', 'is_update', 'is_retrieve', 'is_delete', 'is_org_admin']
        read_only_fields = ['organization_id', 'employee_id', 'is_org_admin']


class OrganizationNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationNotification
        fields = ['permission_notify']


class OrganizationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationCategory
        fields = ['id', 'organization_category']