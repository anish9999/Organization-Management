from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from organization.models import *
from organization.serializers import *
from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet
from organization.utils import *
from organization.permissions import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from organization.client import UserUniqueIdChecker
from organization.publisher import EmployeeRemoved, OrgNotification


from django.db.models.signals import post_save
from django.dispatch import Signal, receiver


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .permissions import IsOwner, UpdatePermission, DeletePermission, RetrievePermission
from .serializers import OrganizationSerializer, OrganizationDetailSerializer
from .utils import get_user_details, generate_id, luhn_algorithm


# class OrganizationViewSet(ModelViewSet):
#     """
#     This viewset is responsible for the CRUD operation of the organization model.
#     """
#     queryset = Organization.objects.all()
#     permission_classes = [IsAuthenticated]

#     def get_serializer_class(self):
#         if self.action in [CrudOperation.LIST, CrudOperation.CREATE]:
#             return OrganizationSerializer
#         return OrganizationDetailSerializer

#     def get_permissions(self):
#         if self.action == CrudOperation.UPDATE:
#             self.permission_classes = [IsAuthenticated, IsOwner | UpdatePermission]
#         elif self.action == CrudOperation.LIST:
#             self.permission_classes = [IsAuthenticated, IsOwner]
#         elif self.action == CrudOperation.DESTROY:
#             self.permission_classes = [IsAuthenticated, IsOwner | DeletePermission]
#         elif self.action == CrudOperation.RETRIEVE:
#             self.permission_classes = [IsAuthenticated, IsOwner | RetrievePermission]
#         else:
#             self.permission_classes = [IsAuthenticated]
#         return super().get_permissions()

#     def get_queryset(self):
#         user_id = get_user_details(self.request)
#         return self.queryset.filter(created_by=user_id)

#     def create(self, request, *args, **kwargs):
#         user_id = get_user_details(self.request)
#         data = request.data
#         established_date = data.get('established_date')
#         no_checksum_number = generate_id(established_date)
#         organization_id = luhn_algorithm(no_checksum_number)

#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)

#         if user_id:
#             unique_id_check = UserUniqueIdChecker(user_id, '').id_call()
#             if unique_id_check['check'] != 'available':
#                 return Response(
#                     data={'status': 'Failed', 'message': 'user email is not available.'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         serializer.save(created_by=user_id, organization_id=organization_id)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    


""" ===================================================================================================================================== """

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from organization.serializers import OrganizationSerializer, OrganizationDetailSerializer
from organization.models import Organization
from organization.utils import get_user_details, generate_id, luhn_algorithm
from rest_framework.response import Response
from rest_framework import status


class OrganizationViewSet(ModelViewSet):
    """
    This viewset is responsible for the CRUD operation of the organization model For testing purpose i omitted person methods.
    """
    queryset = Organization.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'create']:
            return OrganizationSerializer
        return OrganizationDetailSerializer

    def get_queryset(self):
        user_id = get_user_details(self.request)
        return self.queryset.filter(created_by=user_id)

    def create(self, request, *args, **kwargs):
        user_id = get_user_details(self.request)
        data = request.data
        established_date = data.get('established_date')
        no_checksum_number = generate_id(established_date)
        organization_id = luhn_algorithm(no_checksum_number)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        if user_id:
            unique_id_check = UserUniqueIdChecker(user_id, '').id_call()
            if unique_id_check['check'] != 'available':
                return Response(
                    data={'status': 'Failed', 'message': 'user email is not available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer.save(created_by=user_id, organization_id=organization_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    """ ========================================================================================================================= """

class OrganizationEmployeeViewSet(ModelViewSet):
    """
        This viewset is responsible for the CRUD operation of organization employee model
    """
    queryset = OrganizationEmployee.objects.all()

    def get_serializer_class(self):
        if self.action == CrudOperation.LIST or self.action == CrudOperation.CREATE:
            return OrganizationEmployeeSerializer
        return OrganizationEmployeeDetailSerializer

    # def get_permissions(self):
    #     if self.action == CrudOperation.UPDATE:
    #         self.permission_classes = [
    #             IsAuthenticated, IsOwner | UpdatePermission]
    #     elif self.action == CrudOperation.LIST:
    #         self.permission_classes = [
    #             IsAuthenticated, IsOwner | ListPermission]
    #     elif self.action == CrudOperation.DESTROY:
    #         self.permission_classes = [
    #             IsAuthenticated, IsOwner | DeletePermission]
    #     elif self.action == CrudOperation.RETRIEVE:
    #         self.permission_classes = [
    #             IsAuthenticated, IsOwner | RetrievePermission] 
    #     else:
    #         self.permission_classes = [
    #             IsAuthenticated | IsOwner | CreatePermission]
    #     return super().get_permissions()

    def get_queryset(self):
        user_id = get_user_details(self.request)
        org_id = self.kwargs['org_id']
        if Organization.objects.filter(id=org_id).exists():
            # org_unique_id = Organization.objects.get(id=org_id).organization_id
            if OrganizationEmployee.objects.filter(employee_id=user_id, organization_id=org_id).exists():
                return self.queryset.filter(organization_id=org_id)
            else:
                raise serializers.ValidationError({
                    'status': 'failed',
                    'message': 'you do not belongs to this organization'
                })
        else:
            raise serializers.ValidationError({
                'status': 'failed',
                'message': 'organization does not exists.'
            })

    def create(self, request, *args, **kwargs):
        user_id = get_user_details(self.request)
        org_fk_id = self.kwargs['org_id']
        data = request.data
        employee_id = data['employee_id']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        organization_id = Organization.objects.get(id=org_fk_id)
        current_site = get_current_site(request)

        if serializer.is_valid(raise_exception=True):
            if Organization.objects.filter(id=org_fk_id).exists():
                # fk_organization_id = Organization.objects.get(
                #     id=org_fk_id).organization_id
                if OrganizationEmployee.objects.filter(employee_id=user_id, organization_id=org_fk_id).exists():
                    # getting logged in user pk from org emp
                    # logged_user_employee_id = OrganizationEmployee.objects.get(employee_id=user_id, organization_id=org_fk_id).id

                    if OrganizationEmployee.objects.filter(employee_id=user_id, organization_id=org_fk_id, is_org_admin=True) or EmployeePermission.objects.filter(organization_id=org_fk_id, employee_id=user_id, is_create=True):
                        if OrganizationEmployee.objects.filter(organization_id=org_fk_id, employee_id=employee_id).exists():
                            return Response(data={
                                'status': 'failed',
                                'message': 'Employee already exists in this organization.'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        unique_id_check = UserUniqueIdChecker('',
                            employee_id).id_call()

                        # if unique_id_check['check'] == 'unavailable' and unique_id_check['message'] == 'unavailable':
                        #     return Response(data={
                        #             'status': 'failed',
                        #             'message': "user is not available"
                        #     }, status=status.HTTP_403_FORBIDDEN)

                        # elif unique_id_check['check'] == 'unavailable' and unique_id_check['message'] == 'customer':
                        #     return Response(data={
                        #             'status': 'failed',
                        #             'message': "user has already registered as customer"
                        #     }, status=status.HTTP_403_FORBIDDEN)

                        if unique_id_check['check'] == 'available':
                            #taking model instance of organization based on their pk
                            # serializer.save(organization_id=Organization.objects.get(id=org_fk_id))
                            if self.queryset.filter(employee_id=unique_id_check['user_id']).exists():
                                if self.queryset.filter(employee_id=unique_id_check['user_id'], is_org_admin=True).exists():
                                    if self.queryset.filter(employee_id=unique_id_check['user_id'], is_org_admin=False).exists():
                                        return Response(data={
                                            'status': 'failed',
                                            'message': 'Already employee of organization'
                                        }, status=status.HTTP_403_FORBIDDEN)
                                    serializer.validated_data['employee_id'] = unique_id_check['user_id']
                                    user = serializer.save(added_by=user_id, organization_id=Organization.objects.get(id=org_fk_id))

                                    #employee_list of organization to send notification to all employee when new employee is added
                                    employee_list = list(self.queryset.filter(organization_id=org_fk_id).values_list('employee_id', flat=True))

                                    #publishing notification
                                    notification = {
                                        'sender': user_id,
                                        'receiver': employee_list,
                                        'sender_module': 'organization',
                                        'receiver_module': 'organization',
                                        'short_message': 'New Employee added',
                                        'long_message': 'New employee has been added in our organization',
                                        'link': f'http://127.0.0.0.1:8000/api/v1/organization/{org_fk_id}/organization-employee/{user.id}' 
                                    }
                                    OrgNotification('notification', notification)
                                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                                return Response(data={
                                    'status': 'failed',
                                    'message': 'Already employee of organization'
                                })
                            serializer.validated_data['employee_id'] = unique_id_check['user_id']
                            user = serializer.save(added_by=user_id,organization_id=Organization.objects.get(id=org_fk_id))

                            #employee list of organization to send notification to all employee when new employee is added
                            employee_list = list(self.queryset.filter(organization_id=org_fk_id).values_list('employee_id', flat=True))
                           
                            #publishing notification
                            notification = {
                                        'sender': user_id,
                                        'receiver': f'{employee_list}',
                                        'sender_module': 'organization',
                                        'receiver_module': 'organization',
                                        'short_message': 'New Employee added',
                                        'long_message': 'New employee has been added in our organization',
                                        'link': f'http://127.0.0.0.1:8000/api/v1/organization/{org_fk_id}/organization-employee/{user.id}' 
                                    }
                        
                            OrgNotification('notification', notification)
                            return Response(serializer.data, status=status.HTTP_201_CREATED)
                            
                        elif unique_id_check['check'] == 'unavailable' and unique_id_check['message'] == 'customer':
                            return Response(data={
                                    'status': 'failed',
                                    'message': "user has already registered as customer"
                            }, status=status.HTTP_403_FORBIDDEN)

                        organization_id = Organization.objects.get(id=org_fk_id)
                        current_site = get_current_site(request)
                        verify_account(user_id, data, organization_id,current_site)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    return Response(data={
                        'status': 'failed',
                        'message': 'you do not have permission'
                    }, status=status.HTTP_403_FORBIDDEN)

                return Response(data={
                    'status': 'failed',
                    'message': 'you do not belong to this organization'
                }, status=status.HTTP_403_FORBIDDEN)

            return Response(data={
                'status': 'failed',
                'message': 'Organization does not exists.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response(data={
            'status': 'failed',
            'message': 'Bad request.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        user_id = get_user_details(self.request)
        instance = self.get_object()
        instance.delete()
        ex_employee = OrganizationExEmployee(removed_by=user_id,organization_id = instance.organization_id, employee_id = instance.employee_id, position = instance.position, organization_joined_date = instance.organization_joined_date)
        EmployeeRemoved('employee-removed', instance.employee_id)     
        ex_employee.save()

        return Response(data={
            'status': 'success',
            'message': 'Employee removed successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class ExEmployeeView(ListAPIView):
    """
        This class is responsible to show the list of ex employee of the organization
    """
    serializer_class = OrganizationExEmployeeSerializer
    queryset = OrganizationExEmployee.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        org_fk_id = self.kwargs['org_id']
        if self.queryset.filter(organization_id=org_fk_id).exists():
            return self.queryset.filter(organization_id=org_fk_id)


class EmployeePermissionViewSet(ModelViewSet):
    """
        This viewset is responsible for the CRUD operation of employee permission model.
        Only admin of the organization can be accessible to this model
    """
    queryset = EmployeePermission.objects.all()
    serializer_class = EmployeePermissionSerializer

    def get_permissions(self):
        if self.action == CrudOperation.LIST or self.action == CrudOperation.CREATE or self.action == CrudOperation.RETRIEVE or self.action == CrudOperation.UPDATE or self.action == CrudOperation.DESTROY:
            self.permission_classes = [IsAuthenticated, IsOwner]
        return super().get_permissions()

    def get_queryset(self):
        user_id = get_user_details(self.request)
        user_fk_id = self.kwargs['user_id']
        if OrganizationEmployee.objects.filter(id=user_fk_id).exists():
            user_org_id = OrganizationEmployee.objects.get(
                id=user_fk_id).organization_id.pk
            employee_id = OrganizationEmployee.objects.get(
                id=user_fk_id).employee_id

            if user_id == int(employee_id):
                # if self.queryset.filter(organization_id=user_org_id, employee=user_fk_id, is_org_admin=True).exists():
                return self.queryset.filter(organization_id=user_org_id)
            else:
                raise serializers.ValidationError({
                    'status': 'failed',
                    'message': 'you do not belong to this organization'
                })
        else:
            raise serializers.ValidationError({
                'status': 'failed',
                'message': 'you do not have permission'
            })
        
    # def get_object(self, queryset=None):

    #     return super().get_object()

    def update(self, request, *args, **kwargs):
        user_id = get_user_details(self.request)
        user_fk_id = self.kwargs['user_id']
        if OrganizationEmployee.objects.filter(id=user_fk_id).exists():
            user_org_id = OrganizationEmployee.objects.get(
                id=user_fk_id).organization_id
            employee_id = OrganizationEmployee.objects.get(
                id=user_fk_id).employee_id
            if user_id == int(employee_id):
                partial = kwargs.pop('partial', False)
                instance = self.get_object()    
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                receiver_id = [instance.id]

                if OrganizationNotification.objects.filter(employee_id = instance.employee_id, permission_notify=True).exists():
                    notification = {
                            'sender': user_id,
                            'receiver': receiver_id,
                            'sender_module': 'organization',
                            'receiver_module': 'organization',
                            'short_message': 'Permission Updated',
                            'long_message': 'Permission has been updated for you',
                            'link': f'http://127.0.0.0.1:8000/api/v1/organization/{user_id}/organization-employee/{instance.id}' 
                        }
                                    
                    OrgNotification('notification', notification)
                
                    return Response(data={
                        'status': 'successful',
                        'message': 'updated permission with notification release'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(data={
                    'status': 'successful',
                    'message': 'updated permission'
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                'status': 'failed',
                'message': 'You do not belong to this organization'
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data={
                'status': 'failed',
                'message': 'User id doesnot exist'
            }, status=status.HTTP_401_UNAUTHORIZED)


class OrganizationNotificationUpdateView(RetrieveUpdateAPIView):
    """
        This view is responsible for updating notification permission of organization employee
    """
    serializer_class = OrganizationNotificationSerializer
    queryset = OrganizationNotification.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'employee_id'
    lookup_url_kwarg = 'user_id'

    def update(self, request, *args, **kwargs):
        user_id = get_user_details(self.request)
        if self.queryset.filter(employee_id=user_id).exists():
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(data={
                    'status':'success',
                    'message': 'Updated notification toggle'
                }, status=status.HTTP_200_OK)
        return Response(data={
            'status':'failed',
            'message': 'You do not belong to organization'
        }, status=status.HTTP_403_FORBIDDEN)
        

class OrganizationCategoryListView(ListAPIView):
    serializer_class = OrganizationCategorySerializer
    queryset = OrganizationCategory.objects.all()
    # permission_classes = [IsAuthenticated, IsAdminUser]
