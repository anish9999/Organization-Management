import os, sys, pika, django, json
from decouple import config
from sys import path
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
path.append(BASE_DIR/'organizationManagement/settings.py')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organizationManagement.settings')
django.setup()

from organization.models import OrganizationEmployee, Organization
from organization.publisher import OrgNotification

params = pika.URLParameters(config('RABBIT_MQ'))
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.exchange_declare(exchange='invited-user-created', exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)
queue_name  = result.method.queue
channel.queue_bind(exchange='invited-user-created', queue=queue_name)


def InvitedUserConsume(channel, method, properties, body):
    """
        This function is responsible to add employee on organization employee table who has get invitation request
    """
    print(body)
    data = json.loads(body)
    organization_id = Organization.objects.get(id=data[1])
    if data:
        if properties.content_type == 'invited-user-created':
            user = OrganizationEmployee.objects.create(employee_id=data[0], organization_id = organization_id, position=data[2], added_by=data[3])
            user.save()
            
            notification = {
                'sender': data[3],
                'receiver': data[0],
                'sender_module': 'organization',
                'receiver_module': 'organization',
                'short_message': 'New Employee added',
                'long_message': 'New employee has been added in our organization',
                'link': f'http://127.0.0.0.1:8000/api/v1/organization/{organization_id}/organization-employee/{data[0]}'
            }
            OrgNotification(notification)
            print("Employee has been added")
        else:
            print('User has not been added')
    else:
        print('data not found')

        
channel.basic_consume(queue=queue_name, on_message_callback=InvitedUserConsume, auto_ack=True)
print("Started Consuming...")
channel.start_consuming()