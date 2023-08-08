import json
import pika
import uuid
from decouple import config

#to get data from auth_module as per user_id and user_email
class UserUniqueIdChecker(object):
    """
    This is rabbit mq class which is worked as client means the connection is RPC of rabbitmq. This class is responsible for connection between orgnization module and 
    authentication module where this organization module is worked as client and authentication module is working as server

    """
    def __init__(self, user_id, user_email):
        """
            This function run at first and make connection based on routing key and default exchange

            parameters: 'user_id' is for logged in user and 'user_email' is for adding employee
        """
        params = pika.URLParameters(config('RABBIT_MQ'))
        self.connection = pika.BlockingConnection(params)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None
        self.user_id = user_id
        self.user_email = user_email


    def on_response(self, ch, method, props, body):
        """
            This function returns the output requested by this class where it has been called
        """
        if self.corr_id == props.correlation_id:
            data = json.loads(body)
            self.response = data

    def id_call(self):
        """
            This function is responsible to transfer data from this organization module to another where it has been connected i.e. authentication module
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='user_email_check_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=f'{self.user_id},{self.user_email}')
        self.connection.process_data_events(time_limit=None)
        return self.response


