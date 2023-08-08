from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from organization.models import Organization, OrganizationEmployee, OrganizationNotification
import datetime

#create organization creator in employee table for permission
@receiver(post_save, sender=Organization)
def add_employee(sender, instance, created, *args, **kwargs):
    """
        This function is the signal which is responsible to add user (i.e. admin of organization) in organization emplotee model when user set up new organization
    """
    if created:
        instance.organizationemployee_set.create(added_by = instance.created_by ,organization_id=instance.organization_id, employee_id=instance.created_by,
                                                 position='org admin', organization_joined_date = datetime.datetime.now(), role='Admin', is_org_admin=True)
                                                 

@receiver(post_save, sender=OrganizationEmployee)
def add_employee_on_permission_table(sender, instance, created, *args, **kwargs):
    """
        This function is the signal which is responsible to add employee on permission table when any new employee is added on orgnization employee table
    """
    if created:
        if instance.is_org_admin == True:
            # instance.organization_id.id is written because instance.organization_id has foreikey relation so instance.organization_id.id is written to get real id
            instance.employeepermission_set.create(added_by= instance.added_by,organization_id=instance.organization_id.id, employee_id=instance.employee_id, is_org_admin=True, is_create=True, is_list=True, is_update=True, is_retrieve=True, is_delete=True)
        else:
            instance.employeepermission_set.create(added_by= instance.added_by, organization_id=instance.organization_id.id, employee_id=instance.employee_id)

@receiver(post_save, sender=OrganizationEmployee)
def add_employee_on_notification_table(sender, instance, created, *agrs, **kwargs):
    """
        This function is a signal which is responsible to add employee on organization notification model when new employee is added on orgnization employee table
    """
    if created:
        employee_id = instance.employee_id
        OrganizationNotification.objects.create(employee_id=employee_id)