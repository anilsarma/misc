#!/usr/bin/python

import os
import sys
import getopt
import base64
import httplib2
import  argparse

from email.mime.text import MIMEText
#from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from oauth2client import tools
from time import gmtime, strftime
from apiclient.discovery import build

"""
 Pref-requisites:
 pip install --upgrade google-api-python-client
 
 https://console.developers.google.com/flows/enableapi?apiid=gmail  // save the json into the .credentials directory
 
"""

def send_email(gmail_service, to, sender, subject, body):
    # send an email to me
    if os.path.exists(body):
        data = ""
        with open(body, "r") as myfile:
            data = myfile.readlines()
        body = "".join(data)
    email = MIMEText(body)
    email['to'] = to
    email['from'] = sender
    email['subject'] = subject
    email = {'raw': base64.b64encode(email.as_string())}
    result = gmail_service.users().messages().send(userId='me', body=email).execute()
    print(result)

if __name__ == "__main__":
    #default location of downloaded file

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
         os.makedirs(credential_dir)



    parser = argparse.ArgumentParser(parents=[tools.argparser])
    #parser = argparse.ArgumentParser()
    parser.add_argument("--to", help="email address of the recepient", required=True)
    parser.add_argument("--from_gmail", help="email address of the gmail user", required=True)
    parser.add_argument("--subject", help="subject of the email", default="")
    parser.add_argument("--body", help="body of the email", default="")


    args = parser.parse_args()

    #print "args", args
    #flags = parser.parse_args()
    #print flags
    # Path to the client_secret.json file downloaded from the Developer Console
    CLIENT_SECRET_FILE = os.path.join(credential_dir, 'gmail.client_secret.json')

    # Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
    #OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
    #OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.compose'

    # Location of the credentials storage file
    STORAGE = Storage(os.path.join(credential_dir, 'gmail.storage'))

    # Start the OAuth flow to retrieve credentials
    flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
    http = httplib2.Http()

    # Try to retrieve credentials from storage or run the flow to generate them
    credentials = STORAGE.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, STORAGE, args, http=http)

    # for x in  dir(STORAGE):
    #     print x, getattr(STORAGE, x)
    #
    # exit(0)
    # Authorize the httplib2.Http object with our credentials
    http = credentials.authorize(http)

    # Build the Gmail service from discovery
    gmail_service = build('gmail', 'v1', http=http)

    send_email( gmail_service, args.to, args.from_gmail,  args.subject, args.body)
    print args.body


