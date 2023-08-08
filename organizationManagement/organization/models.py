from django.db import models
from django.utils import timezone

class OrganizationCategory(models.Model):
    """
        This is organization category model
    """
    organization_category = models.CharField(max_length=200, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.organization_category
    
    class Meta:
        verbose_name_plural = "Organization Category" 


class Organization(models.Model):
    """
        This is organization model
    """
    created_by = models.IntegerField()
    organization_id = models.CharField(unique=True, max_length=20)
    organization_name = models.CharField(max_length=255, unique=True)
    established_date = models.DateField()
    organization_category = models.ForeignKey(OrganizationCategory, on_delete=models.CASCADE)
    organization_email = models.EmailField(max_length=255, unique=True)
    contact_number = models.CharField(max_length=15)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    zip_code = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = "Organization"


class OrganizationEmployee(models.Model):
    """
        This is organization employee model
    """
    CHOICES =[
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
        ('Ex-employee', 'Ex-employee')
    ]
    added_by = models.CharField(max_length=255)
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    organization_joined_date = models.DateField(default=timezone.now)
    role = models.CharField(max_length=50, choices=CHOICES, default='Employee')
    updated_at = models.DateTimeField(auto_now=True)
    added_at = models.DateTimeField(default=timezone.now)
    is_org_admin = models.BooleanField(default=False)

    def __str__(self):
        return str(self.employee_id)

    class Meta:
        verbose_name_plural = "Organization Employee"


class EmployeePermission(models.Model):
    """
        This is employee permission model
    """
    added_by = models.CharField(max_length=255)
    organization_id = models.IntegerField()
    employee_id = models.ForeignKey(OrganizationEmployee, on_delete=models.CASCADE)
    is_org_admin = models.BooleanField(default=False)
    is_create = models.BooleanField(default=False)
    is_list = models.BooleanField(default=False)
    is_update = models.BooleanField(default=False)
    is_retrieve = models.BooleanField(default=False)
    is_delete =  models.BooleanField(default=False)
    added_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name_plural = "Organization Employee Permissions"


class OrganizationExEmployee(models.Model):
    """
        This is ex employee model
    """
    removed_by = models.CharField(max_length=255)
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    organization_joined_date = models.DateField(default=timezone.now)
    role = models.CharField(max_length=15, default='Ex-employee')
    removed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.employee_id)

    class Meta:
        verbose_name_plural = "Organization Ex-employee"


class OrganizationNotification(models.Model):
    """
        This is notification permission model
    """
    employee_id = models.CharField(max_length=255)
    permission_notify = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.employee_id)
