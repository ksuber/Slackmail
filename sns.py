import boto3
import json
import logging
import os
import smtplib
from base64 import b64decode
from urlparse import parse_qs

ENCRYPTED_EXPECTED_TOKEN = os.environ['kmsEncryptedToken']

kms = boto3.client('kms')
expected_token = kms.decrypt(CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext']
logger = logging.getLogger()
logger.setLevel(logging.INFO)
sns_client = boto3.client('sns')

def respond(err, res=None):
    return err.message if err else res

def lambda_handler(event, context):
    print event
    params = parse_qs(event['body'])
    print params
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match expected", token)
        return respond(Exception('Invalid request token'))
    sns_response = sns_client.publish(
            TopicArn= 'arn:aws:sns:us-east-1:773500838498:slackmail',
            Message=json.dumps({'default': json.dumps(params)}),
            MessageStructure='json'
        )

    return respond(None, "Working on your request")
