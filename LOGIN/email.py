from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def EmailVerification(email,user):
    uuid=urlsafe_base64_encode(force_bytes(user.pk))
    token =default_token_generator.make_token(user)
    link=f'http://127.0.0.1:8000/verify/{uuid}/{token}/'
    subject='verification mail'
    body=f'your link is {link}'
    email_from=settings.EMAIL_HOST_USER
    reciptent_list=[email]

    send_mail(subject,body,email_from,reciptent_list)



def TempEmployeeCredentials(email,password):

    subject='Login credentials'
    body=f'your credentials are email:{email},password:{password}'
    email_from=settings.EMAIL_HOST_USER
    reciptent_list=[email]
    send_mail(subject,body,email_from,reciptent_list)

