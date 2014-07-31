#!/usr/bin/python

#
# Script to download attachements from gmail
# not very good but works, enhance ments need to the 
# message id storage, need to think of a better method then just
# writing the entire dictionary to file everytime.

import os
import sys
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
# dclare a filter
query = 'has:attachment'
emailTo='x@yahoo.com'
emailFrom='x@gmail.com'

parser = argparse.ArgumentParser(parents=[tools.argparser])
flags = parser.parse_args()

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = store_dir + 'client_secret.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
#OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'

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

class MessageStore:
  
  def __init__(self, filename):
    self.filename = filename
    self.store = {}
    if os.path.exists(self.filename):
      f = open(self.filename, "r")
      lines = []
      for l in f:
	l = l.rstrip('\n')
	self.store[l]=l
      f.close()

  def save(self, id):
    self.store[id]=id

  def has(self,id):
    if id in self.store:
	return True
    return False

  def commit(self):
    f = open(self.filename, "w")
    for k in self.store.keys():
    	f.write( k )
	f.write('\n')
    f.close()

   

class TokenManager:
  def __init__(self, filename):
    self.filename = filename


  def getToken(self):
    return None

    # the emails are in latest order so using this is useless
    if os.path.exists(self.filename):
      f = open(self.filename, "r")
      lines = []
      for l in f:
        lines.append(l)
      f.close()
      if( len(lines)>0):
        return lines[0]
    return None

  def saveToken(self, token):
    f = open(self.filename, "w")
    f.write( token )
    f.close()

# end of class TokenManager

email ='following files were downloaded'

def get_attachment(msg):
  files = []
  if not( 'payload' in msg and 'parts' in msg['payload']):
    return files

  for part in msg['payload']['parts']:
    #print "had parts", part
    if part['filename']:
      file_data= None
      filename = part['filename']
      if not re.match(r'some_pattern_data.+', filename):
              print "skip ..", filename
              continue
      path = ''.join([store_dir, part['filename']])
      if os.path.exists( path ):
              print "already completed ..", filename
              continue;

      print "downloading ..", filename
      if part['body']['attachmentId']:
              attach = gmail_service.users().messages().attachments().get( messageId=msg['id'],id=part['body']['attachmentId'], userId='me' ).execute()
              file_data = base64.urlsafe_b64decode(attach['data'].encode('UTF-8'))
              f = open(path + ".part", 'w')
              f.write(file_data)
              f.close()
              os.rename(path + ".part", path )
              files.append( path )
              continue
      try:
              file_data = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8'))
      except:
              print "except ..", filename
              #print msg
              #print part
              #file_data = base64.urlsafe_b64decode(msg['body']['data'].encode('UTF-8'))
              continue
      path = ''.join(["./", part['filename']])
      print path
  return files

token_manager = TokenManager('page_token.data')
next_token = token_manager.getToken()

msgstore = MessageStore(store_dir + "msg_id_store.dat");
#print next_token

files = []
while True:
  messages = None
  if next_token:
    messages = gmail_service.users().messages().list(userId='me', q=query, pageToken=next_token).execute()
  else:
    messages = gmail_service.users().messages().list(userId='me', q=query).execute()

  #print messages
  # use the next token to get all emails, do that later TODO:: etay.
  if messages['messages']:
    for message in messages['messages']:
      msgid = message['id']
      if msgstore.has(msgid)==True:
	print "skipping message %s already processed" % msgid
	continue
      msgstore.save(msgid)
      msg = gmail_service.users().messages().get(id=message['id'], userId='me').execute()
      tmp_files = get_attachment( msg )
      files.extend(tmp_files)
      
  if 'nextPageToken'  in messages:
    token_manager.saveToken( messages['nextPageToken'] )
    next_token = messages['nextPageToken']
  else:
    next_token = None

  if next_token == None:
    break

  msgstore.commit()
  print "looping ..... "
 # sys.exit(0)
# testing code we really want to do this after completion of the message loop incase of
# errors	
#token_manager.saveToken( messages['nextPageToken'] )
msgstore.commit()
if len(files)>0:
  email = 'file(s) downloaded %d'% len(files)
  for f in files:
    email = email +"\n\t" +  f;
  print 'sending email '
  send_email( gmail_service, emailTo, emailFrom, 'Bot run ' + getpass.getuser() + "@" + socket.gethostname() 
              + "  " +  strftime("%Y%m%d%H%M%S", gmtime()), email)
  print email


