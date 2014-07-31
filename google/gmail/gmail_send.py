#!/usr/bin/python

import os
import sys
import getopt
import re
import base64
import httplib2
import getpass
import  argparse
import socket

from email.mime.text import MIMEText
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from oauth2client import tools
from time import gmtime, strftime


#default location of downloaded file
store_dir = "./"

email ='this is a test email to your user id of choice'
emailTo='x@yahoo.com'
emailFrom='x@gmail.com'
emailSubject='Test email'
opts, args = getopt.getopt(sys.argv[1:], "ht:f:s:b:", ["help", "to=", "from=", "subject=", "body=", "noauth_local_webserver"])
for o, a in opts:
        if o in ("-t", "--to"):
		emailTo=a
		sys.argv.remove(o)
		sys.argv.remove(a)
        elif o in ("-f", "--from"):
		emailFrom=a
		sys.argv.remove(o)
		sys.argv.remove(a)
        elif o in ("-s", "--subject"):
		emailSubject=a
		sys.argv.remove(o)
		sys.argv.remove(a)
        elif o in ("-b", "--body"):
		email=a
		sys.argv.remove(o)
		sys.argv.remove(a)

parser = argparse.ArgumentParser(parents=[tools.argparser])
flags = parser.parse_args()

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = store_dir + 'client_secret.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
#OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
#OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.compose'

# Location of the credentials storage file
STORAGE = Storage(store_dir + 'gmail.storage')

# Start the OAuth flow to retrieve credentials
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run_flow(flow, STORAGE, flags, http=http)

# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)

# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)


def send_email(gmail_service, to, sender, subject, body):
  # send an email to me
  email = MIMEText(body)
  email['to'] = to
  email['from'] = sender
  email['subject'] = subject
  email = {'raw': base64.b64encode(email.as_string())}
  gmail_service.users().messages().send(userId='me', body=email) .execute()




send_email( gmail_service, emailTo, emailFrom,  emailSubject, email)
print email


