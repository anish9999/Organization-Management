from django.urls import path, include
from organization.views import *
from rest_framework import routers

app_name = 'organization'

router = routers.DefaultRouter()

router.register('organization', OrganizationViewSet, basename='organization')
router.register('(?P<org_id>[^/.]+)/organization-employee', OrganizationEmployeeViewSet, basename='organization-employee')
router.register('(?P<user_id>[^/.]+)/employee-permission', EmployeePermissionViewSet, basename='employee-permission')

urlpatterns = [
    path('',include(router.urls)),
    path('<int:org_id>/organization-ex-employee/', ExEmployeeView.as_view(), name='organization-ex-employee'),
    path('organization-notification/<int:user_id>/', OrganizationNotificationUpdateView.as_view(), name='organization-notification'),
    path('organization-category', OrganizationCategoryListView.as_view(), name='organization-category'),
]
