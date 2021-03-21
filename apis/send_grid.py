def path_hack():
    import os, sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    # print('path added:', sys.path[0])

path_hack()

import json
from apis import authentication
import urllib.request
from urllib.request import urlopen
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_mail(from_email:str, to_emails:list, subject:str, html_content:str):
    '''
    Uses the SendGrid API to send an email. 
        * from_email(str):      Required. The sender's email
        * to_emails(list):      Required: A list or of recipient emails, string is fine for one recipient.
        * subject(str):         The subject of the email 
        * html_content(str):    Text or HTML to be included in the body of the email.
    Returns True if the email was successfully sent, False otherwise.
    '''
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content
    )
    try:
        token = authentication.get_token('https://www.apitutor.org/sendgrid/key')
        sg = SendGridAPIClient(token)
        sg.send(message)
        # print('Email sent.')
        return True
        # response = sg.send(message)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
    except Exception as e:
        # print(e)
        return False