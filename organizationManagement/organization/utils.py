import random
from rest_framework_simplejwt.tokens import AccessToken
from enum import Enum
import threading
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from organization.models import Organization



def generate_id(established_date):
    """
        This function is responsible to generate unique id of 11 length for each organization which will be based on lunh algorithm
    """
    date = str(established_date)
    new_date = date.replace('-', '')
    final_date = new_date[2:]
    abc = random.sample(range(0, 9), 4)
    b = ''
    for i in abc:
        b += str(i)
    a = '{}{}'.format(final_date, b)
    arr = []
    for i in a:
        arr.append(int(i))
    return arr

def luhn_algorithm(number):
    """
        This function is responsible to make valid unique id of organization based on lunh algorith and also validate the number
    """
    check_sum = 0

    check_offset = (len(number) + 1) % 2
    for i, n in enumerate(number):
        if (i + check_offset) % 2 == 0:
            n_ = n*2
            check_sum += n_ - 9 if n_ > 9 else n_
        else:
            check_sum += n

    remainder = check_sum % 10

    if remainder == 0:
        new_number = number + [0]
    else:
        new_number = number + [10 - remainder]

    final_organization_id = ''
    for i in new_number:
        final_organization_id += str(i)

    return final_organization_id


def get_user_details(request):
    """
        This function is responsible to get user id from token
    """
    token_header = request.META.get('HTTP_AUTHORIZATION')
    token = token_header.replace("Bearer ", '')
    access_token_str = AccessToken(token)
    user_id = access_token_str['user_id']
    return user_id


class CrudOperation(str, Enum):
    LIST = 'list'
    CREATE = 'create'
    UPDATE = 'update'
    RETRIEVE = 'retrieve'
    DESTROY = 'destroy'


def verify_account(user_id ,employee, organization_id, current_site):
    """
        This function is responsible to send email to invited user who do not have accounts on our system
    """
    added_by = urlsafe_base64_encode(force_bytes(user_id)) 
    employee_email = urlsafe_base64_encode(force_bytes(employee['employee_id']))
    organization = urlsafe_base64_encode(force_bytes(organization_id))
    position = urlsafe_base64_encode(force_bytes(employee['position']))

    link = f'127.0.0.1:8000/api/v1/accounts/register/?invited_to={employee_email}&organization={organization}&position={position}&added_by={added_by}'
    url = 'http://'+link
    email_subject = "Sign up invitation"
    email_body = f"Hi, {employee['employee_id']}\n{organization_id.organization_name} has invited you to join his organization. Please click the below link for sign up first.\n"+url
    email = EmailMessage(
            email_subject,
            email_body,
            'noreply@gmail.com',
            [employee['employee_id']]
        )
    EmailThread(email).start()

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)
