from rest_framework.permissions import BasePermission
from organization.utils import get_user_details
from organization.models import EmployeePermission, OrganizationEmployee
from rest_framework.response import Response
# def permission(request):
#     print(request.user)


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        user_id = get_user_details(request)

        if EmployeePermission.objects.filter(employee_id=user_id, is_org_admin=True):
            return True
        return False

class CreatePermission(BasePermission):

    def has_permission(self, request, view):
        user_id = get_user_details(request)

        if EmployeePermission.objects.filter(employee_id=user_id, is_create=True):
            return False
        return False


class ListPermission(BasePermission):

    def has_permission(self, request, view):
        user_id = get_user_details(request)

        if EmployeePermission.objects.filter(employee_id=user_id, is_list=True):
            return True
        return False



class UpdatePermission(BasePermission):

    def has_permission(self, request, view):
        user_id = get_user_details(request)
        # user_id = OrganizationEmployee.objects.get(employee_id=user_id).id

        if EmployeePermission.objects.filter(employee_id=user_id, is_update=True, is_retrieve=True, is_list=True):
            return True
        return False


class RetrievePermission(BasePermission):

    def has_permission(self, request, view):
        user_id = get_user_details(request)
        
        if EmployeePermission.objects.filter(employee_id=user_id, is_retrieve=True, is_list=True):
            return True
        return False


class DeletePermission(BasePermission):

    def has_permission(self, request, view):
        user_id = get_user_details(request)
        # user_id = OrganizationEmployee.objects.get(employee_id=user_id).id
        
        if EmployeePermission.objects.filter(employee_id=user_id, is_delete=True, is_retrieve=True, is_list=True):
            return True
        return False