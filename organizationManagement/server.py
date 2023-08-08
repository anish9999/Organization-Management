import pika
from sys import path
import os
from pathlib import Path
import django
import json

BASE_DIR = Path(__file__).resolve().parent.parent
path.append(BASE_DIR/'organizationManagement/settings.py')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organizationManagement.settings')
django.setup()

from organization.models import Organization, OrganizationEmployee
from decouple import config


params = pika.URLParameters(config('RABBIT_MQ'))
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='user_id_for_org')
# channel.queue_declare(queue='unique_id_emp_queue')

#connection between subscription and organization to return organization id
def user_id_for_org(ch, method, props, body):
    id =str(body)
    received_data = id.split("'")
    final_received_data = received_data[1]
    user_id_and_org_id = final_received_data.split(",")
    user_id = user_id_and_org_id[0]
    org_id = user_id_and_org_id[1]
    if Organization.objects.filter(organization_id=org_id).exists():
        org_fk_id = Organization.objects.get(organization_id=org_id).id
        if Organization.objects.filter(created_by=user_id, organization_id=org_id).exists():
            if OrganizationEmployee.objects.filter(employee_id=user_id, organization_id=org_fk_id, is_org_admin=True).exists():
                data = Organization.objects.get(organization_id=org_id)
                response = {
                    'source': 'organization',
                    'destination': 'subscription',
                    'id': data.id,
                    'check': 'available',
                }
            else:
                response = {
                    'source': 'organization',
                    'destination': 'subscription',
                    'check': 'unavailable'
                }
        else:
            response = {
                'source': 'organization',
                'destination': 'subscription',
                'check': 'Not Match'
            }
    else:
            response = {
                'source': 'organization',
                'destination': 'subscription',
                'check': 'organization unavailable'
            }
    print(response)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='user_id_for_org',
                      on_message_callback=user_id_for_org)



def employee_queue(ch, method, props, body):
    id = str(body)
    received_data = id.split("'")
    final_received_data = received_data[1]
    employee_id_and_org_id = final_received_data.split(",")
    employee_id = employee_id_and_org_id[0]
    org_unique_id = employee_id_and_org_id[1]
    if Organization.objects.filter(id=org_unique_id).exists():
        if OrganizationEmployee.objects.filter(employee_id=employee_id, organization_id=org_unique_id).exists():
            response = {
                'check': 'available',
            }
        else:
            response = {
                'check': 'unavailable'
            }
    else:
        response = {
            'check': 'organization unavailable'
        }
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.queue_declare(queue='inventory_employee_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='inventory_employee_queue',
                      on_message_callback=employee_queue)


channel.queue_declare(queue='menu_configuration_employee_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='menu_configuration_employee_queue',
                      on_message_callback=employee_queue)


channel.queue_declare(queue='order_employee_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='order_employee_queue',
                      on_message_callback=employee_queue)


channel.queue_declare(queue='schedule_employee_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='schedule_employee_queue',
                      on_message_callback=employee_queue)
                      

channel.queue_declare(queue='qr_employee_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='qr_employee_queue',
                      on_message_callback=employee_queue)


def admin_queue(ch, method, props, body):
    id = str(body)
    received_data = id.split("'")
    final_received_data = received_data[1]
    org_id_and_admin_id = final_received_data.split(",")
    org_unique_id = org_id_and_admin_id[0]
    admin_id = org_id_and_admin_id[1]

    if OrganizationEmployee.objects.filter(employee_id=admin_id, organization_id=org_unique_id, is_org_admin=True).exists():
        response = {
                    'check': 'available',
                }        
    else:
        response = {
                    'check': 'unavailable'
                }
    
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.queue_declare(queue='inventory_admin_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='inventory_admin_queue',
                      on_message_callback=admin_queue)


channel.queue_declare(queue='menu_configuration_admin_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='menu_configuration_admin_queue',
                      on_message_callback=admin_queue)
                      

channel.queue_declare(queue='order_admin_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='order_admin_queue',
                      on_message_callback=admin_queue)
                      

channel.queue_declare(queue='schedule_admin_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='schedule_admin_queue',
                      on_message_callback=admin_queue)


channel.queue_declare(queue='qr_admin_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='qr_admin_queue',
                      on_message_callback=admin_queue)



print('start consuming')
channel.start_consuming()

