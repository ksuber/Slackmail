from slackclient import SlackClient
import json
import logging
import os
import smtplib

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Mail password
MAIL_SECRET = os.environ["MAIL_SECRET"]
SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]


def make_string(value):
    ''' Pulls the values from the sns message and creates
        usable variables to pass to other functions'''
    new_value = str(json.dumps(value))
    new_value = new_value[2:-2]
    return new_value


def respond(err, res=None):
    ''' Generic response part of orginal template left in as an
        example for sending a response'''
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def sendemail(message, from_addr, subject='Slack Helpdesk Request',
              to_addr_list=['helpdesk@aspph.org'], cc_addr_list=[],
              login='slack@aspph.org', password=MAIL_SECRET,
              smtpserver='smtp.office365.com:587'):
    ''' Sends email after putting together the headers most of the values
        provided will be defaults. normal usage will require a message and a to
        address'''
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
    # headers and message above below sending message
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems


def get_email(user_id):
    ''' Makes and api call using a user_id to return user info
        and extract email address'''
    sc = SlackClient(SLACK_API_TOKEN)
    user_info = sc.api_call(
        "users.info",
        user=user_id
    )
    email = user_info['user']['profile']['email']
    return email


def response(channel_id, user_id, text):
    ''' Makes api call to post reply message, this is
        a delayed response after intial response'''
    sc2 = SlackClient(SLACK_API_TOKEN)
    sc2.api_call(
        "chat.postMessage",
        channel=channel_id,
        user_id=user_id,
        text=text,
        username='Jetson',
        icon_url='https://s3.amazonaws.com/aspph-internal/slackjetson.jpg'
    )


def lambda_handler(event, context):
    ''' Main lambda function parses sns notification for needed info'''

    message = json.loads(event['Records'][0]['Sns']['Message'])
    user_id = message['user_id']
    user_id = make_string(user_id)
    command = message['command']
    command = make_string(command)
    channel = message['channel_name']
    channel = make_string(channel)
    channel_id = message['channel_id']
    channel_id = make_string(channel_id)
    command_text = message['text']
    command_text = make_string(command_text)
    payload = "Your helpdesk ticket has been submitted"
    # Get email from api
    email = get_email(user_id)
    # Send mail and issues response to user
    sendemail(command_text, email)
    response(channel_id, user_id, payload)
