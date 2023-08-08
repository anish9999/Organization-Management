import pika
import json
from decouple import config


params = pika.URLParameters(config('RABBIT_MQ'))
connection = pika.BlockingConnection(params)
channel = connection.channel()


channel.exchange_declare(exchange='employee-removed', exchange_type='fanout')
channel.exchange_declare(exchange='notification', exchange_type='direct')

# to send message to all modules that employee has been removed
def EmployeeRemoved(method, body):
    """
        This is rabbitmq file function which is responsible for removing employee from all modules related to this organization when employee is removed from the organizatione employee modle
    """
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='employee-removed', routing_key='employee-removed', body=json.dumps(body), properties=properties)
    print('Employee removed')

# publish notification
def OrgNotification(method, body):
    """
        This function is responsible to publish notification to notification module when new event is trigger
    """
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='notification', routing_key='notification', body=json.dumps(body), properties=properties)
    print('Notification published')

